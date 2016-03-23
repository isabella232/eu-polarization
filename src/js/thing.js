var fm = require('./fm');
var throttle = require('./throttle');
var features = require('./detectFeatures')();
var d3 = require('d3');
var request = require('d3-request');
var _ = require('lodash');

var MOBILE_THRESHOLD = 600;

var chartData = null;
var dataSeries = [];

function init () {
    d3.csv('./data/test.csv', function(err, data) {
		chartData = formatData(data);

        console.log(chartData);

		update();
	});
}

var formatData = function(data) {
    data.forEach(function(d) {

        for (var key in d) {
            d[key] = +d[key];
        }
    });

    /*
     * Restructure tabular data for easier charting.
     */
    for (var column in data[0]) {
        if (column == 'year') {
            continue;
        }

        dataSeries.push({
            'name': column,
            'values': data.map(function(d) {
                return {
                    'year': d['year'],
                    'value': d[column]
                };
            })
        });
    }
}

function update () {
    var width = $('#interactive-content').width();

	if (width <= MOBILE_THRESHOLD) {
		isMobile = true;
	} else {
		isMobile = false;
	}

	renderChart({
		container: '#chart',
		width: width,
		data: dataSeries
	});

	// adjust iframe for dynamic content
	fm.resize()
}

function resize() {
	update()
}

/*
 * Render a chart.
 */
var renderChart = function(config) {
	/*
	 * Setup chart container.
	 */
	var margins = {
		top: 10,
		right: 5,
		bottom: 25,
		left: 50
	};

    var aspectRatio = 1.2;

	// Calculate actual chart dimensions
	var chartWidth = config['width'] - margins['left'] - margins['right'];
	var chartHeight = Math.ceil(config['width'] / aspectRatio) - margins['top'] - margins['bottom'];

	// Clear existing graphic (for redraw)
	var containerElement = d3.select(config['container']);
	containerElement.html('');

	/*
	 * Create the root SVG element.
	 */
	var chartWrapper = containerElement.append('div')
		.attr('class', 'graphic-wrapper');

	var chartElement = chartWrapper.append('svg')
		.attr('width', chartWidth + margins['left'] + margins['right'])
		.attr('height', chartHeight + margins['top'] + margins['bottom'])
		.append('g')
		.attr('transform', 'translate(' + margins['left'] + ',' + margins['top'] + ')');

	/*
	 * Create D3 scale objects.
	 */
	var xScale = d3.scale.linear()
		.range([0, chartWidth])
		.domain([0, 10]);

    console.log(config['data'])

	var yScale = d3.scale.linear()
		.range([chartHeight, 0])
		.domain([2015, 1980]);

	/*
	 * Create D3 axes.
	 */
	var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient('bottom')
    .ticks(5)

	var yAxis = d3.svg.axis()
		.scale(yScale)
		.orient('left')
		.tickFormat(function(d, i) {
			return d;
		});

	/*
	 * Render axes to chart.
	 */
	var xAxisElement = chartElement.append('g')
		.attr('class', 'x axis')
		.attr('transform', makeTranslate(0, chartHeight))
		.call(xAxis);

	var yAxisElement = chartElement.append('g')
		.attr('class', 'y axis')
		.call(yAxis)

	/*
	 * Render grid to chart.
	 */
    var xAxisGrid = function() {
 		return xAxis;
 	};

 	xAxisElement.append('g')
 		.attr('class', 'x grid')
 		.call(xAxisGrid()
 			.tickSize(-chartHeight, 0)
 			.tickFormat('')
 		);

	var yAxisGrid = function() {
		return yAxis;
	};

	yAxisElement.append('g')
		.attr('class', 'y grid')
		.call(yAxisGrid()
			.tickSize(-chartWidth, 0)
			.tickFormat('')
		);

	/*
	 * Render lines to chart.
	 */
     var line = d3.svg.line()
        .interpolate('monotone')
        .x(function(d) {
            console.log(d['value'], xScale(d['value']))
            return xScale(d['value']);
        })
        .y(function(d) {
            return yScale(d['year']);
        });

    chartElement.append('path')
        .attr('class', 'zero-line')
        .attr('d', function(d) {
            return line([
                { 'year': 1980, 'value': 5 },
                { 'year': 2015, 'value': 5 }
            ]);
        });

    chartElement.append('text')
        .attr('class', 'left')
        .attr('x', xScale(4.75))
        .attr('y', yScale(1982))
        .attr('text-anchor', 'end')
        .text('◀ Political left');

    chartElement.append('text')
        .attr('class', 'left')
        .attr('x', xScale(5.25))
        .attr('y', yScale(1982))
        .text('Political right ▶');

    chartElement.append('g')
        .attr('class', 'lines')
        .selectAll('path')
        .data(config['data'])
        .enter()
        .append('path')
            .attr('class', function(d, i) {
                return 'line ' + classify(d['name']);
            })
            .attr('stroke', function(d) {
                // return colorScale(d['name']);
            })
            .attr('d', function(d) {
                return line(d['values']);
            });
}

/*
 * Convert arbitrary strings to valid css classes.
 * via: https://gist.github.com/mathewbyrne/1280286
 */
var classify = function(str) {
	return str.toLowerCase()
		.replace(/\s+/g, '-')					 // Replace spaces with -
		.replace(/[^\w\-]+/g, '')			 // Remove all non-word chars
		.replace(/\-\-+/g, '-')				 // Replace multiple - with single -
		.replace(/^-+/, '')						 // Trim - from start of text
		.replace(/-+$/, '');						// Trim - from end of text
}

/*
 * Convert key/value pairs to a style string.
 */
var formatStyle = function(props) {
	var s = '';

	for (var key in props) {
		s += key + ': ' + props[key].toString() + '; ';
	}

	return s;
}

/*
 * Create a SVG tansform for a given translation.
 */
var makeTranslate = function(x, y) {
	var transform = d3.transform();

	transform.translate[0] = x;
	transform.translate[1] = y;

	return transform.toString();
}

var throttleRender = throttle(resize, 250);

$(document).ready(function () {
	// adjust iframe for loaded content
	fm.resize()
	$(window).resize(throttleRender);
	init();
});
