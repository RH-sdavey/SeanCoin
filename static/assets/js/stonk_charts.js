const maxValue = chart_data.price_vol_diff.dayHigh;
const valueToPercent = (val) => Math.round(val * 100) / maxValue;
const percentToValue = (val) => Math.round(val * maxValue) / 100
const fiftyTwoWeekmaxValue = chart_data.price_vol_diff.fiftyTwoHigh;

const chart_config = {
    "chart": {
        "chart": {
            toolbar: {
                show: false
            },
            type: 'area',
            height: 250,
            zoom: {
                enabled: true
            }
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: "straight"
        },
        yaxis: {
            opposite: true
        },
        xaxis: {
            type: 'datetime',
            categories: chart_data.dates.range
        },
        legend: {
            horizontalAlign: 'left'
        }
    },
}

const common_chart_config = {
    chart: chart_config.chart.chart,
    dataLabels: chart_config.chart.dataLabels,
    stroke: chart_config.chart.stroke,
    legend: chart_config.chart.legend,
    yaxis: chart_config.chart.yaxis,
    xaxis: chart_config.chart.xaxis,
};
    <!--PRICE CHART-- >
new ApexCharts(document.querySelector("#priceChart"), {
    series: [
        {
            name: chart_data.name,
            type: 'area',
            data: chart_data.price_vol_diff.prices
        }, {
            name: chart_data.spy.name,
            type: "line",
            data: chart_data.spy.prices
        }
    ],
    subtitle: {
        align: 'left',
        text: "Price"
    },
    ...common_chart_config
}).render();
<!--/PRICE CHART -->
    <!--VOLUME CHART-- >
new ApexCharts(document.querySelector("#volumeChart"), {
    series: [{
        name: chart_data.name,
        data: chart_data.price_vol_diff.volume
    }, ],
    subtitle: {
        text: 'Volume',
        align: 'left'
    },
    ...common_chart_config
}).render();
<!--/VOLUME CHART -->
<!--DIFF CHART-- >
new ApexCharts(document.querySelector("#diffChart"), {
    series: [{
        name: chart_data.name,
        data: chart_data.price_vol_diff.open_close_diff
    }, ],
    subtitle: {
        text: 'Price Diff',
        align: 'left'
    },
    ...common_chart_config
}).render();
 <!--/DIFF CHART -->

<!--CURRENT PRICE GAUGE-- >
new ApexCharts(document.querySelector("#priceGauge"), {
    series: [100],
    chart: {
        height: 280,
        type: 'radialBar',
        toolbar: {
            show: false
        }
    },
    plotOptions: {
        radialBar: {
            startAngle: -135,
            endAngle: 225,
            hollow: {
                margin: 0,
                size: '70%',
                background: '#fff',
                image: undefined,
                imageOffsetX: 0,
                imageOffsetY: 0,
                position: 'front',
                dropShadow: {
                    enabled: true,
                    top: 3,
                    left: 0,
                    blur: 4,
                    opacity: 0.24
                }
            },
            track: {
                background: '#fff',
                strokeWidth: '67%',
                margin: 0, // margin is in pixels
                dropShadow: {
                    enabled: true,
                    top: -3,
                    left: 0,
                    blur: 4,
                    opacity: 0.35
                }
            },

            dataLabels: {
                show: true,
                name: {
                    offsetY: -10,
                    show: true,
                    color: '#888',
                    fontSize: '17px'
                },
                value: {
                    formatter: function(val) {
                        return parseInt(chart_data.price_vol_diff.dayCurrent);
                    },
                    color: '#111',
                    fontSize: '36px',
                    show: true,
                }
            }
        }
    },
    fill: {
        type: 'gradient',
        gradient: {
            shade: 'dark',
            type: 'horizontal',
            shadeIntensity: 0.5,
            gradientToColors: ['#ABE5A1'],
            inverseColors: true,
            opacityFrom: 1,
            opacityTo: 1,
            stops: [0, 100]
        }
    },
    stroke: {
        lineCap: 'round'
    },
    labels: ['Current Price'],
}).render();
<!--/CURRENT PRICE GAUGE -->

high_low_radial_common_config = {
    chart: {
        height:280,
        type: 'radialBar',
    },
    plotOptions: {
        radialBar: {
            offsetY: 0,
            startAngle: 0,
            endAngle: 270,
            hollow: {
                margin: 5,
                size: '30%',
                background: 'transparent',
                image: undefined,
            },
            dataLabels: {
                name: {
                    show: false,
                },
                value: {
                    show: true,
                    formatter: percentToValue,
                }
            }
        }
    },
    colors: ['#d9534f', '#0275d8', '#5cb85c'],
    legend: {
        show: true,
        floating: true,
        fontSize: '8px',
        position: 'left',
        offsetX: 0,
        offsetY: 15,
        labels: {
            useSeriesColors: true,
        },
        markers: {
            size: 0
        },
        formatter: function(seriesName, opts) {
            return seriesName
        },
        itemMargin: {
            vertical: 3
        }
    },
    responsive: [{
        breakpoint: 480,
        options: {
            legend: {
                show: false
            }
        }
    }]
};

    <!--DAY LOW + CURRENT + HIGH-- >
new ApexCharts(document.querySelector("#dayhighLowChart"), {
    series: [valueToPercent(chart_data.price_vol_diff.dayLow),
        valueToPercent(chart_data.price_vol_diff.dayCurrent),
        valueToPercent(maxValue)
    ],
    labels: ['dayLow', 'currentPrice', 'dayHigh'],
    ...high_low_radial_common_config
}).render();
    <!--/DAY LOW+CURRENT+HIGH-->


    <!--52 LOW + CURRENT + HIGH-- >
new ApexCharts(document.querySelector("#fiftyTwoWeekHighLowChart"), {
    series: [valueToPercent(chart_data.price_vol_diff.fiftyTwoLow),
             valueToPercent(chart_data.price_vol_diff.dayCurrent),
             valueToPercent(fiftyTwoWeekmaxValue)
            ],
    labels: ['fiftyTwoWeekLow', 'currentPrice', 'fiftyTwoWeekHigh'],
    ...high_low_radial_common_config
}).render();
    <!--/52 LOW+CURRENT+HIGH-->

financial_chart_common_config = {
    chart: {
        "chart": {
            toolbar: {
                show: false
            }
        },
        height: 280,
        type: "line",
        stacked: false
    },
    dataLabels: {
        enabled: true
    },
    colors: ["#FF1654", "#247BA0"],
    tooltip: {
        shared: false,
        intersect: true,
        x: {
            show: false
        }
    },
    legend: {
        horizontalAlign: "left",
        offsetX: 40
    },
    stroke: {
        width: [4, 4]
    },
    plotOptions: {
        bar: {
            columnWidth: "20%"
        }
    },
    xaxis: {
        categories: chart_data.dates.q_dates
    },
    axisTicks: {
        show: true
    },
}

financial_chart_first_yaxis = {
    axisTicks: financial_chart_common_config.axisTicks,
    axisBorder: {
        show: true,
        color: "#FF1654"
    },
    labels: {
        style: {
            colors: "#FF1654"
        }
    }
};

financial_chart_second_yaxis = {
    opposite: true,
    axisTicks: financial_chart_common_config.axisTicks,
    axisBorder: {
        show: true,
        color: "#247BA0"
    },
    labels: {
        style: {
            colors: "#247BA0"
        }
    },
};

new ApexCharts(document.querySelector("#quarterlyEarningsRevenueChart"), {
    title: {
        text: 'Quarterly Earnings and Revenue',
        align: 'left'
    },
    series: [{
            name: "Earnings",
            data: chart_data.earnings.earnings
        },
        {
            name: "Revenue",
            data: chart_data.revenue.revenue
        }
    ],

    yaxis: [{
            ...financial_chart_first_yaxis,
            title: {
                text: "Earnings",
                style: {
                    color: financial_chart_first_yaxis.labels.style.colors
                }
            }
        },
        {
            ...financial_chart_second_yaxis,
            title: {
                text: "Revenue",
                style: {
                    color: financial_chart_second_yaxis.labels.style.colors
                }
            }
        }
    ],
    ...financial_chart_common_config
}).render();


new ApexCharts(document.querySelector("#quarterlyEarningsGrowthChart"), {
    title: {
        text: 'Quarterly Earnings Growth',
        align: 'left'
    },
    series: [{
            name: "Estimated",
            data: chart_data.earnings.est_earnings
        },
        {
            name: "Actual",
            data: chart_data.earnings.actual_earnings
        }
    ],

    yaxis: [{
            ...financial_chart_first_yaxis,
            title: {
                text: "Estimated",
                style: {
                    color: financial_chart_first_yaxis.labels.style
                        .colors
                }
            }
        },
        {
            ...financial_chart_second_yaxis,
            title: {
                text: "Actual",
                style: {
                    color: financial_chart_second_yaxis.labels.style
                        .colors
                }
            }
        }
    ],
    ...financial_chart_common_config
}).render();

new ApexCharts(document.querySelector("#yearlyEarningsRevenueChart"), {
    title: {
        text: 'Yearly Earnings and Revenue',
        align: 'left'
    },
    series: [{
            name: "Earnings",
            data: chart_data.earnings.y_earn
        },
        {
            name: "Revenue",
            data: chart_data.revenue.y_revenue
        }
    ],

    yaxis: [{
            ...financial_chart_first_yaxis,
            title: {
                text: "Earnings",
                style: {
                    color: financial_chart_first_yaxis.labels.style
                        .colors
                }
            }
        },
        {
            ...financial_chart_second_yaxis,
            title: {
                text: "Revenue",
                style: {
                    color: financial_chart_second_yaxis.labels.style
                        .colors
                }
            }
        }
    ],
    ...financial_chart_common_config,
    xaxis: {
        categories: chart_data.dates.y_dates
    },
}).render();



new ApexCharts(document.querySelector("#recommendationChart"), {
labels: chart_data.latest_rec.rec,
        series: chart_data.latest_rec.count,
        chart: {
          type: 'polarArea',
          height: 350,
          toolbar: {
            show: true
          }
        },
        stroke: {
          colors: ['#fff']
        },
        fill: {
          opacity: 0.8
        }
      }).render();

    <!--DAILY HIGH/LOW DIFF CHART-- >
new ApexCharts(document.querySelector("#highLowDiffChart"), {
    series: [
        {
            name: chart_data.name,
            type: 'area',
            data: chart_data.price_vol_diff.high_low_diff
        }
    ],
    subtitle: {
        align: 'left',
        text: "Daily High/Low Price Diff",
    },
    ...common_chart_config
}).render();
<!--/PRICE CHART -->