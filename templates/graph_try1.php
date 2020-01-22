<?php 
include 'dvastnavbar.php';
?>

<!doctype html>
<!DOCTYPE html>
<html>
<head>
	<title>Dmand Graph </title>
	<!-- <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	 --><!-- <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
	 --><!-- <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
 -->	<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
	<script src="https://code.highcharts.com/highcharts.js"></script>
	<script src="https://code.highcharts.com/modules/exporting.js"></script>
	<script src="https://code.highcharts.com/modules/export-data.js"></script>
</head>
<body><!-- 'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/usdeur.json' -->
	<div id="container" style="min-width: 310px; height: 400px; width: 80%; margin: 0 auto"></div>
	<script type="text/javascript">
		$.getJSON("https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/usdeur.json"
    ,
    function (data) {
        Highcharts.setOptions({
            colors: ['#86bc24', '#000000']
        });

        Highcharts.chart('container', {
            chart: {
                backgroundColor: '#000000',
                zoomType: 'x',
                resetZoomButton: {
                theme: {
                    fill: '#000000',
                    stroke: '#ffffff',
                    r: 0,
                    style: {
                        color: '#ffffff'
                    },
                    states: {
                        hover: {
                            fill: '#86bc24',
                            style: {
                                color: 'white'
                            }
                        }
                    }
                }
        }
            },
            title: {
                text: 'Demand Change',
                style: {
                    color: '#FFFFFF',
                    fontWeight: 'bold'
                }
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in',
                    style: {
                    color: '#FFFFFF'
                }
            },
            xAxis: {
                lineColor: '#FFFFFF',
                type: 'datetime'
            },
            yAxis: {
                lineColor: '#FFFFFF',
                title: {
                    text: 'Demand',
                    color: '#ffffff'
                },
                gridLineWidth: 0
            },
            legend: {
                enabled: false
            },
            credits: {
                enabled: false
            },
            tooltip: {
                xDateFormat: '%b %e %H:%M'
            },
            series: [{
                type: 'area',
                name: 'USD to EUR',
                data: data,
                fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {
                        radius: 1
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null

            }],
            exporting: {
                buttons: {
                    contextButton: {
                        symbolStroke: "grey",
                        theme: {
                            fill:"#000000",
                            states: {
                                hover: {
                                    fill: '#000000',
                                    stroke: '#86bc24'

                                },
                                select: {
                                    fill: '#86bc24'
                                }
                            }
                        }
                    }
                }
            }
        });
    }
);
	</script>

</body>
</html>