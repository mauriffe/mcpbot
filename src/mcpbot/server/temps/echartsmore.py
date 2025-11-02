from mcp import types
from fastmcp import Context
import logging
import json
from typing import List, Dict, Any, Literal, Optional

logger = logging.getLogger(__name__)


def _json_serialize(obj):
    """Helper function to ensure proper JSON serialization."""
    return json.loads(json.dumps(obj))


def register_chart_generator_tools(mcp):
    @mcp.tool(
        name="generate_line_chart",
        description="Generate a line chart configuration for displaying trends over time or categories. Perfect for showing temperature trends, stock prices, sales over time, etc.",
        tags={"visualization", "charts", "echarts", "line"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Line Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_line_chart(
            title: str,
            labels: List[str],
            values: List[float],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            smooth: bool = True,
            show_area: bool = False,
            ctx: Context = None
    ) -> dict:
        """
        Generate a line chart configuration.

        Args:
            title: Chart title
            labels: List of labels for X-axis (e.g., ["Mon", "Tue", "Wed"])
            values: List of numeric values corresponding to labels
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            smooth: Whether to use smooth curves
            show_area: Whether to show area under the line

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri"]
            values = [20, 22, 25, 23, 21]
        """
        try:
            if len(labels) != len(values):
                return {
                    "success": False,
                    "error": "labels and values must have the same length"
                }

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "3%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": labels,
                    "name": x_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 30
                },
                "yAxis": {
                    "type": "value",
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": [{
                    "data": values,
                    "type": "line",
                    "smooth": smooth,
                    "lineStyle": {"width": 3},
                    "itemStyle": {"color": "#3498db"}
                }]
            }

            if show_area:
                chart_config["series"][0]["areaStyle"] = {}

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            # Ensure proper JSON serialization (converts Python True/False to JSON true/false)
            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating line chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_bar_chart",
        description="Generate a bar chart configuration for comparing values across categories. Perfect for showing sales by region, survey results, comparisons, etc.",
        tags={"visualization", "charts", "echarts", "bar"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Bar Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_bar_chart(
            title: str,
            labels: List[str],
            values: List[float],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            horizontal: bool = False,
            color: str = "#3498db",
            ctx: Context = None
    ) -> dict:
        """
        Generate a bar chart configuration.

        Args:
            title: Chart title
            labels: List of labels for categories (e.g., ["Q1", "Q2", "Q3"])
            values: List of numeric values corresponding to labels
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            horizontal: If True, creates horizontal bars
            color: Bar color in hex format (e.g., "#3498db")

        Returns:
            dict: Complete chart configuration ready for display_chart tool
        """
        try:
            if len(labels) != len(values):
                return {
                    "success": False,
                    "error": "labels and values must have the same length"
                }

            if horizontal:
                chart_config = {
                    "title": {
                        "text": title,
                        "left": "center",
                        "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                    },
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "grid": {
                        "left": "3%",
                        "right": "4%",
                        "bottom": "3%",
                        "containLabel": True
                    },
                    "xAxis": {
                        "type": "value",
                        "name": x_axis_label
                    },
                    "yAxis": {
                        "type": "category",
                        "data": labels,
                        "name": y_axis_label
                    },
                    "series": [{
                        "data": values,
                        "type": "bar",
                        "itemStyle": {"color": color}
                    }]
                }
            else:
                chart_config = {
                    "title": {
                        "text": title,
                        "left": "center",
                        "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                    },
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "grid": {
                        "left": "3%",
                        "right": "4%",
                        "bottom": "3%",
                        "containLabel": True
                    },
                    "xAxis": {
                        "type": "category",
                        "data": labels,
                        "name": x_axis_label,
                        "nameLocation": "middle",
                        "nameGap": 30
                    },
                    "yAxis": {
                        "type": "value",
                        "name": y_axis_label,
                        "nameLocation": "middle",
                        "nameGap": 50
                    },
                    "series": [{
                        "data": values,
                        "type": "bar",
                        "itemStyle": {"color": color}
                    }]
                }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            # Ensure proper JSON serialization (converts Python True/False to JSON true/false)
            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating bar chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_pie_chart",
        description="Generate a pie chart configuration for showing proportions and percentages. Perfect for market share, budget breakdown, survey results, etc.",
        tags={"visualization", "charts", "echarts", "pie"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Pie Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_pie_chart(
            title: str,
            labels: List[str],
            values: List[float],
            description: str = "",
            show_legend: bool = True,
            donut: bool = False,
            ctx: Context = None
    ) -> dict:
        """
        Generate a pie chart configuration.

        Args:
            title: Chart title
            labels: List of labels for pie slices (e.g., ["Product A", "Product B"])
            values: List of numeric values corresponding to labels
            description: Optional description text
            show_legend: Whether to show the legend
            donut: If True, creates a donut chart (pie with hole in center)

        Returns:
            dict: Complete chart configuration ready for display_chart tool
        """
        try:
            if len(labels) != len(values):
                return {
                    "success": False,
                    "error": "labels and values must have the same length"
                }

            pie_data = [
                {"value": value, "name": label}
                for label, value in zip(labels, values)
            ]

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{a} <br/>{b}: {c} ({d}%)"
                },
                "series": [{
                    "name": title,
                    "type": "pie",
                    "radius": ["40%", "70%"] if donut else "60%",
                    "center": ["50%", "55%"],
                    "data": pie_data,
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    },
                    "label": {
                        "formatter": "{b}: {d}%"
                    }
                }]
            }

            if show_legend:
                chart_config["legend"] = {
                    "orient": "vertical",
                    "left": "left",
                    "top": "middle"
                }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            # Ensure proper JSON serialization (converts Python True/False to JSON true/false)
            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating pie chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_scatter_plot",
        description="Generate a scatter plot configuration for showing correlations and distributions. Perfect for showing relationships between two variables. Provide x_values and y_values as separate lists.",
        tags={"visualization", "charts", "echarts", "scatter"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Scatter Plot Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_scatter_plot(
            title: str,
            x_values: List[float],
            y_values: List[float],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            color: str = "#e74c3c",
            ctx: Context = None
    ) -> dict:
        """
        Generate a scatter plot configuration.

        Args:
            title: Chart title
            x_values: List of X-axis values (e.g., [1, 2, 3, 4, 5])
            y_values: List of Y-axis values (e.g., [55, 65, 70, 75, 85])
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            color: Point color in hex format (e.g., "#e74c3c")

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            x_values = [1, 2, 3, 4, 5]
            y_values = [55, 65, 70, 75, 85]
        """
        try:
            if len(x_values) != len(y_values):
                return {
                    "success": False,
                    "error": "x_values and y_values must have the same length"
                }

            scatter_data = [[x, y] for x, y in zip(x_values, y_values)]

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": f"{x_axis_label}: {{c0}}<br/>{y_axis_label}: {{c1}}"
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "3%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "value",
                    "name": x_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 30,
                    "splitLine": {"show": True}
                },
                "yAxis": {
                    "type": "value",
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50,
                    "splitLine": {"show": True}
                },
                "series": [{
                    "type": "scatter",
                    "data": scatter_data,
                    "symbolSize": 12,
                    "itemStyle": {"color": color}
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            # Ensure proper JSON serialization (converts Python True/False to JSON true/false)
            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating scatter plot: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_multi_series_chart",
        description="Generate a multi-series line or bar chart for comparing multiple data series. Perfect for revenue vs expenses, multiple product comparisons, etc. Provide series_names and series_data as separate lists.",
        tags={"visualization", "charts", "echarts", "multi-series"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Multi-Series Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_multi_series_chart(
            title: str,
            categories: List[str],
            series_names: List[str],
            series_data: List[List[float]],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            chart_type: str = "line",
            stacked: bool = False,
            ctx: Context = None
    ) -> dict:
        """
        Generate a multi-series chart configuration.

        Args:
            title: Chart title
            categories: List of category labels for X-axis (e.g., ["Jan", "Feb", "Mar"])
            series_names: List of series names (e.g., ["Revenue", "Expenses"])
            series_data: List of data arrays, one for each series (e.g., [[120, 132, 101], [80, 90, 85]])
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            chart_type: "line" or "bar"
            stacked: Whether to stack the series

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            categories = ["Jan", "Feb", "Mar"]
            series_names = ["Revenue", "Expenses"]
            series_data = [[120, 132, 101], [80, 90, 85]]
        """
        try:
            if len(series_names) != len(series_data):
                return {
                    "success": False,
                    "error": "series_names and series_data must have the same length"
                }

            for i, data in enumerate(series_data):
                if len(data) != len(categories):
                    return {
                        "success": False,
                        "error": f"series_data[{i}] length must match categories length"
                    }

            default_colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

            series_config = []
            for idx, (name, data) in enumerate(zip(series_names, series_data)):
                series_item = {
                    "name": name,
                    "type": chart_type,
                    "data": data,
                    "itemStyle": {
                        "color": default_colors[idx % len(default_colors)]
                    }
                }

                if stacked:
                    series_item["stack"] = "Total"
                    if chart_type == "line":
                        series_item["areaStyle"] = {}

                series_config.append(series_item)

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow" if chart_type == "bar" else "cross"}
                },
                "legend": {
                    "data": series_names,
                    "top": "bottom"
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "12%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": categories,
                    "name": x_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 30
                },
                "yAxis": {
                    "type": "value",
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": series_config
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            # Ensure proper JSON serialization (converts Python True/False to JSON true/false)
            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating multi-series chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_area_chart",
        description="Generate a stacked or overlapping area chart for showing cumulative trends or comparing multiple series over time. Perfect for traffic sources, revenue streams, etc.",
        tags={"visualization", "charts", "echarts", "area"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Area Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_area_chart(
            title: str,
            categories: List[str],
            series_names: List[str],
            series_data: List[List[float]],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            stacked: bool = True,
            ctx: Context = None
    ) -> dict:
        """
        Generate an area chart configuration.

        Args:
            title: Chart title
            categories: List of category labels for X-axis
            series_names: List of series names
            series_data: List of data arrays, one for each series
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            stacked: Whether to stack the areas

        Returns:
            dict: Complete chart configuration ready for display_chart tool
        """
        try:
            if len(series_names) != len(series_data):
                return {
                    "success": False,
                    "error": "series_names and series_data must have the same length"
                }

            default_colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6", "#1abc9c"]

            series_config = []
            for idx, (name, data) in enumerate(zip(series_names, series_data)):
                series_item = {
                    "name": name,
                    "type": "line",
                    "data": data,
                    "areaStyle": {},
                    "smooth": True,
                    "itemStyle": {
                        "color": default_colors[idx % len(default_colors)]
                    }
                }

                if stacked:
                    series_item["stack"] = "Total"

                series_config.append(series_item)

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "legend": {
                    "data": series_names,
                    "top": "bottom"
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "12%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": categories,
                    "boundaryGap": False,
                    "name": x_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 30
                },
                "yAxis": {
                    "type": "value",
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": series_config
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating area chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_gauge_chart",
        description="Generate a gauge/speedometer chart for displaying single metric values like progress, completion rate, KPIs, scores, etc. Perfect for dashboards.",
        tags={"visualization", "charts", "echarts", "gauge"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Gauge Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_gauge_chart(
            title: str,
            value: float,
            min_value: float = 0,
            max_value: float = 100,
            description: str = "",
            unit: str = "%",
            ctx: Context = None
    ) -> dict:
        """
        Generate a gauge chart configuration.

        Args:
            title: Chart title (also used as the metric name)
            value: Current value to display
            min_value: Minimum value of the gauge
            max_value: Maximum value of the gauge
            description: Optional description text
            unit: Unit symbol (e.g., "%", "°C", "km/h")

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_gauge_chart(
                title="Completion Rate",
                value=75.5,
                min_value=0,
                max_value=100,
                unit="%"
            )
        """
        try:
            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "series": [{
                    "type": "gauge",
                    "min": min_value,
                    "max": max_value,
                    "progress": {
                        "show": True,
                        "width": 18
                    },
                    "axisLine": {
                        "lineStyle": {
                            "width": 18
                        }
                    },
                    "axisTick": {
                        "show": False
                    },
                    "splitLine": {
                        "length": 15,
                        "lineStyle": {
                            "width": 2,
                            "color": "#999"
                        }
                    },
                    "axisLabel": {
                        "distance": 25,
                        "color": "#999",
                        "fontSize": 12
                    },
                    "anchor": {
                        "show": True,
                        "showAbove": True,
                        "size": 20,
                        "itemStyle": {
                            "borderWidth": 5
                        }
                    },
                    "title": {
                        "show": False
                    },
                    "detail": {
                        "valueAnimation": True,
                        "fontSize": 30,
                        "offsetCenter": [0, "70%"],
                        "formatter": f"{{value}}{unit}"
                    },
                    "data": [{
                        "value": value,
                        "name": title
                    }]
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating gauge chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_radar_chart",
        description="Generate a radar/spider chart for comparing multiple variables across different categories. Perfect for skill assessments, product comparisons, performance metrics.",
        tags={"visualization", "charts", "echarts", "radar"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Radar Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_radar_chart(
            title: str,
            indicators: List[str],
            series_names: List[str],
            series_data: List[List[float]],
            max_values: List[float] = None,
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a radar chart configuration.

        Args:
            title: Chart title
            indicators: List of indicator names (e.g., ["Speed", "Power", "Defense"])
            series_names: List of series names (e.g., ["Player A", "Player B"])
            series_data: List of data arrays, one for each series
            max_values: Optional list of max values for each indicator (default: auto)
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_radar_chart(
                title="Player Comparison",
                indicators=["Speed", "Power", "Defense", "Stamina", "Technique"],
                series_names=["Player A", "Player B"],
                series_data=[[80, 90, 70, 85, 75], [75, 85, 80, 70, 90]]
            )
        """
        try:
            if len(series_names) != len(series_data):
                return {
                    "success": False,
                    "error": "series_names and series_data must have the same length"
                }

            # Build indicator configuration
            if max_values and len(max_values) == len(indicators):
                indicator_config = [
                    {"name": name, "max": max_val}
                    for name, max_val in zip(indicators, max_values)
                ]
            else:
                # Auto-calculate max values
                all_values = [val for series in series_data for val in series]
                max_val = max(all_values) * 1.2 if all_values else 100
                indicator_config = [
                    {"name": name, "max": max_val}
                    for name in indicators
                ]

            default_colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]

            series_config = []
            for idx, (name, data) in enumerate(zip(series_names, series_data)):
                series_config.append({
                    "value": data,
                    "name": name,
                    "itemStyle": {
                        "color": default_colors[idx % len(default_colors)]
                    },
                    "areaStyle": {
                        "opacity": 0.3
                    }
                })

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "legend": {
                    "data": series_names,
                    "top": "bottom"
                },
                "radar": {
                    "indicator": indicator_config,
                    "shape": "polygon",
                    "splitNumber": 5,
                    "splitArea": {
                        "show": True,
                        "areaStyle": {
                            "color": ["rgba(114, 172, 209, 0.2)", "rgba(114, 172, 209, 0.4)"]
                        }
                    },
                    "axisLine": {
                        "lineStyle": {
                            "color": "rgba(114, 172, 209, 0.8)"
                        }
                    },
                    "splitLine": {
                        "lineStyle": {
                            "color": "rgba(114, 172, 209, 0.8)"
                        }
                    }
                },
                "series": [{
                    "type": "radar",
                    "data": series_config
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating radar chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_heatmap",
        description="Generate a heatmap for visualizing data intensity across two dimensions. Perfect for correlation matrices, time-based patterns, activity levels.",
        tags={"visualization", "charts", "echarts", "heatmap"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Heatmap Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_heatmap(
            title: str,
            x_labels: List[str],
            y_labels: List[str],
            data: List[List[float]],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            color_scheme: str = "blues",
            ctx: Context = None
    ) -> dict:
        """
        Generate a heatmap configuration.

        Args:
            title: Chart title
            x_labels: Labels for X-axis (columns)
            y_labels: Labels for Y-axis (rows)
            data: 2D array of values [y][x] (rows of columns)
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            color_scheme: Color scheme ("blues", "reds", "greens", "purples")

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_heatmap(
                title="Weekly Activity",
                x_labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
                y_labels=["Morning", "Afternoon", "Evening"],
                data=[[5, 8, 12, 10, 7], [15, 20, 18, 22, 16], [8, 10, 14, 12, 9]]
            )
        """
        try:
            # Flatten data into [x, y, value] format
            heatmap_data = []
            for y_idx, row in enumerate(data):
                for x_idx, value in enumerate(row):
                    heatmap_data.append([x_idx, y_idx, value])

            # Color schemes
            color_schemes = {
                "blues": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594"],
                "reds": ["#fff5f0", "#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#99000d"],
                "greens": ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#005a32"],
                "purples": ["#fcfbfd", "#efedf5", "#dadaeb", "#bcbddc", "#9e9ac8", "#807dba", "#6a51a3", "#4a1486"]
            }

            colors = color_schemes.get(color_scheme, color_schemes["blues"])

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "position": "top",
                    "formatter": lambda
                        params: f"{y_labels[params['data'][1]]}, {x_labels[params['data'][0]]}: {params['data'][2]}"
                },
                "grid": {
                    "height": "60%",
                    "top": "15%",
                    "left": "15%"
                },
                "xAxis": {
                    "type": "category",
                    "data": x_labels,
                    "splitArea": {"show": True},
                    "name": x_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 30
                },
                "yAxis": {
                    "type": "category",
                    "data": y_labels,
                    "splitArea": {"show": True},
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "visualMap": {
                    "min": min([item[2] for item in heatmap_data]) if heatmap_data else 0,
                    "max": max([item[2] for item in heatmap_data]) if heatmap_data else 100,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "5%",
                    "inRange": {
                        "color": colors
                    }
                },
                "series": [{
                    "type": "heatmap",
                    "data": heatmap_data,
                    "label": {
                        "show": True
                    },
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    }
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating heatmap: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_funnel_chart",
        description="Generate a funnel chart for visualizing stages in a process with decreasing values. Perfect for sales funnels, conversion rates, application stages.",
        tags={"visualization", "charts", "echarts", "funnel"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Funnel Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_funnel_chart(
            title: str,
            labels: List[str],
            values: List[float],
            description: str = "",
            show_percentages: bool = True,
            ctx: Context = None
    ) -> dict:
        """
        Generate a funnel chart configuration.

        Args:
            title: Chart title
            labels: Stage names (e.g., ["Visits", "Sign Ups", "Purchases"])
            values: Values for each stage (should be decreasing)
            description: Optional description text
            show_percentages: Whether to show conversion percentages

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_funnel_chart(
                title="Sales Funnel",
                labels=["Website Visits", "Sign Ups", "Trials", "Purchases"],
                values=[10000, 3500, 1200, 450]
            )
        """
        try:
            if len(labels) != len(values):
                return {
                    "success": False,
                    "error": "labels and values must have the same length"
                }

            funnel_data = [
                {"value": value, "name": label}
                for label, value in zip(labels, values)
            ]

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}: {c}"
                },
                "legend": {
                    "orient": "vertical",
                    "left": "left",
                    "top": "middle"
                },
                "series": [{
                    "type": "funnel",
                    "left": "25%",
                    "top": "15%",
                    "bottom": "10%",
                    "width": "50%",
                    "min": 0,
                    "max": max(values) if values else 100,
                    "minSize": "0%",
                    "maxSize": "100%",
                    "sort": "descending",
                    "gap": 2,
                    "label": {
                        "show": True,
                        "position": "inside",
                        "formatter": "{b}: {c}" if not show_percentages else "{b}\n{c} ({d}%)"
                    },
                    "labelLine": {
                        "length": 10,
                        "lineStyle": {
                            "width": 1,
                            "type": "solid"
                        }
                    },
                    "itemStyle": {
                        "borderColor": "#fff",
                        "borderWidth": 1
                    },
                    "emphasis": {
                        "label": {
                            "fontSize": 16
                        }
                    },
                    "data": funnel_data
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating funnel chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_box_plot",
        description="Generate a box plot (box and whisker chart) for showing statistical distributions. Perfect for showing quartiles, outliers, and data spread.",
        tags={"visualization", "charts", "echarts", "boxplot"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Box Plot Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_box_plot(
            title: str,
            categories: List[str],
            data: List[List[float]],
            y_axis_label: str = "",
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a box plot configuration.

        Args:
            title: Chart title
            categories: Category names for each box (e.g., ["Group A", "Group B"])
            data: List of arrays, each containing [min, Q1, median, Q3, max] for a box
            y_axis_label: Label for Y-axis
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_box_plot(
                title="Test Score Distribution",
                categories=["Class A", "Class B", "Class C"],
                data=[[50, 65, 75, 85, 95], [45, 60, 70, 80, 90], [55, 70, 80, 90, 98]]
            )
        """
        try:
            if len(categories) != len(data):
                return {
                    "success": False,
                    "error": "categories and data must have the same length"
                }

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item",
                    "axisPointer": {"type": "shadow"}
                },
                "grid": {
                    "left": "10%",
                    "right": "10%",
                    "bottom": "15%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": categories,
                    "boundaryGap": True,
                    "nameGap": 30,
                    "splitArea": {"show": False},
                    "splitLine": {"show": False}
                },
                "yAxis": {
                    "type": "value",
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50,
                    "splitArea": {"show": True}
                },
                "series": [{
                    "type": "boxplot",
                    "data": data,
                    "itemStyle": {
                        "color": "#3498db",
                        "borderColor": "#2c3e50"
                    }
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating box plot: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_sankey_diagram",
        description="Generate a Sankey diagram for visualizing flow between nodes. Perfect for energy flows, budget allocation, traffic sources, supply chains.",
        tags={"visualization", "charts", "echarts", "sankey"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Sankey Diagram Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_sankey_diagram(
            title: str,
            nodes: List[str],
            links: List[Dict[str, Any]],
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a Sankey diagram configuration.

        Args:
            title: Chart title
            nodes: List of node names
            links: List of connections with format: [{"source": "A", "target": "B", "value": 10}, ...]
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_sankey_diagram(
                title="Website Traffic Flow",
                nodes=["Homepage", "Products", "Checkout", "Contact", "Exit"],
                links=[
                    {"source": "Homepage", "target": "Products", "value": 1000},
                    {"source": "Homepage", "target": "Contact", "value": 200},
                    {"source": "Products", "target": "Checkout", "value": 300},
                    {"source": "Products", "target": "Exit", "value": 700}
                ]
            )
        """
        try:
            node_data = [{"name": node} for node in nodes]

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item",
                    "triggerOn": "mousemove"
                },
                "series": [{
                    "type": "sankey",
                    "data": node_data,
                    "links": links,
                    "emphasis": {
                        "focus": "adjacency"
                    },
                    "lineStyle": {
                        "color": "gradient",
                        "curveness": 0.5
                    },
                    "label": {
                        "fontSize": 12
                    }
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating sankey diagram: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_treemap",
        description="Generate a treemap for visualizing hierarchical data with nested rectangles. Perfect for disk space usage, budget breakdowns, portfolio composition.",
        tags={"visualization", "charts", "echarts", "treemap"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Treemap Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_treemap(
            title: str,
            data: List[Dict[str, Any]],
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a treemap configuration.

        Args:
            title: Chart title
            data: Hierarchical data structure with format:
                  [{"name": "Category", "value": 100, "children": [{"name": "Item", "value": 50}, ...]}]
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_treemap(
                title="Storage Usage",
                data=[
                    {
                        "name": "Documents",
                        "value": 500,
                        "children": [
                            {"name": "PDFs", "value": 300},
                            {"name": "Word", "value": 200}
                        ]
                    },
                    {
                        "name": "Media",
                        "value": 1500,
                        "children": [
                            {"name": "Photos", "value": 800},
                            {"name": "Videos", "value": 700}
                        ]
                    }
                ]
            )
        """
        try:
            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "formatter": "{b}: {c}"
                },
                "series": [{
                    "type": "treemap",
                    "data": data,
                    "leafDepth": 2,
                    "label": {
                        "show": True,
                        "formatter": "{b}"
                    },
                    "upperLabel": {
                        "show": True,
                        "height": 30
                    },
                    "itemStyle": {
                        "borderColor": "#fff",
                        "borderWidth": 2,
                        "gapWidth": 2
                    },
                    "levels": [
                        {
                            "itemStyle": {
                                "borderWidth": 0,
                                "gapWidth": 5
                            }
                        },
                        {
                            "itemStyle": {
                                "gapWidth": 1
                            }
                        }
                    ]
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating treemap: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_sunburst_chart",
        description="Generate a sunburst chart for visualizing hierarchical data in a radial layout. Perfect for organizational structures, file systems, category breakdowns.",
        tags={"visualization", "charts", "echarts", "sunburst"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Sunburst Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_sunburst_chart(
            title: str,
            data: List[Dict[str, Any]],
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a sunburst chart configuration.

        Args:
            title: Chart title
            data: Hierarchical data with format:
                  [{"name": "Root", "value": 100, "children": [{"name": "Child", "value": 50}, ...]}]
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_sunburst_chart(
                title="Company Organization",
                data=[
                    {
                        "name": "Company",
                        "children": [
                            {
                                "name": "Engineering",
                                "value": 50,
                                "children": [
                                    {"name": "Frontend", "value": 20},
                                    {"name": "Backend", "value": 30}
                                ]
                            },
                            {
                                "name": "Sales",
                                "value": 30,
                                "children": [
                                    {"name": "Direct", "value": 15},
                                    {"name": "Partners", "value": 15}
                                ]
                            }
                        ]
                    }
                ]
            )
        """
        try:
            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item"
                },
                "series": [{
                    "type": "sunburst",
                    "data": data,
                    "radius": ["15%", "90%"],
                    "itemStyle": {
                        "borderRadius": 7,
                        "borderWidth": 2,
                        "borderColor": "#fff"
                    },
                    "label": {
                        "rotate": "radial"
                    }
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating sunburst chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_candlestick_chart",
        description="Generate a candlestick chart for financial data. Perfect for stock prices, showing open/close/high/low values over time.",
        tags={"visualization", "charts", "echarts", "candlestick", "financial"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Candlestick Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_candlestick_chart(
            title: str,
            dates: List[str],
            data: List[List[float]],
            y_axis_label: str = "Price",
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a candlestick chart configuration.

        Args:
            title: Chart title
            dates: List of date labels
            data: List of [open, close, low, high] values for each date
            y_axis_label: Label for Y-axis
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_candlestick_chart(
                title="Stock Price",
                dates=["2024-01", "2024-02", "2024-03"],
                data=[
                    [100, 110, 95, 115],   # [open, close, low, high]
                    [110, 105, 100, 120],
                    [105, 115, 102, 125]
                ]
            )
        """
        try:
            if len(dates) != len(data):
                return {
                    "success": False,
                    "error": "dates and data must have the same length"
                }

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "cross"
                    },
                    "formatter": lambda
                        params: f"{params[0]['name']}<br/>Open: {params[0]['data'][0]}<br/>Close: {params[0]['data'][1]}<br/>Low: {params[0]['data'][2]}<br/>High: {params[0]['data'][3]}"
                },
                "grid": {
                    "left": "10%",
                    "right": "10%",
                    "bottom": "15%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": dates,
                    "boundaryGap": False,
                    "axisLine": {"onZero": False},
                    "splitLine": {"show": False},
                    "min": "dataMin",
                    "max": "dataMax"
                },
                "yAxis": {
                    "scale": True,
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50,
                    "splitArea": {"show": True}
                },
                "series": [{
                    "type": "candlestick",
                    "data": data,
                    "itemStyle": {
                        "color": "#2ecc71",
                        "color0": "#e74c3c",
                        "borderColor": "#2ecc71",
                        "borderColor0": "#e74c3c"
                    }
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating candlestick chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_parallel_coordinates",
        description="Generate a parallel coordinates chart for visualizing multi-dimensional data. Perfect for comparing multiple variables across different items.",
        tags={"visualization", "charts", "echarts", "parallel"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Parallel Coordinates Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_parallel_coordinates(
            title: str,
            dimensions: List[str],
            data: List[List[float]],
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a parallel coordinates chart configuration.

        Args:
            title: Chart title
            dimensions: List of dimension names
            data: List of data points, each with values for all dimensions
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_parallel_coordinates(
                title="Car Comparison",
                dimensions=["Price", "MPG", "Horsepower", "Comfort", "Safety"],
                data=[
                    [25000, 30, 200, 8, 9],
                    [35000, 25, 300, 9, 10],
                    [20000, 35, 150, 7, 8]
                ]
            )
        """
        try:
            # Build dimension schema
            parallel_axis = []
            for idx, dim_name in enumerate(dimensions):
                # Calculate min and max for each dimension
                dim_values = [row[idx] for row in data if idx < len(row)]
                if dim_values:
                    parallel_axis.append({
                        "dim": idx,
                        "name": dim_name,
                        "min": min(dim_values) * 0.9,
                        "max": max(dim_values) * 1.1
                    })

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "item"
                },
                "parallelAxis": parallel_axis,
                "parallel": {
                    "left": "10%",
                    "right": "15%",
                    "bottom": "10%",
                    "top": "15%",
                    "parallelAxisDefault": {
                        "type": "value",
                        "nameLocation": "end",
                        "nameGap": 20
                    }
                },
                "series": [{
                    "type": "parallel",
                    "lineStyle": {
                        "width": 2,
                        "opacity": 0.5
                    },
                    "data": data
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating parallel coordinates: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_waterfall_chart",
        description="Generate a waterfall chart for showing cumulative effect of sequential values. Perfect for financial statements, budget changes, inventory changes.",
        tags={"visualization", "charts", "echarts", "waterfall"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Waterfall Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_waterfall_chart(
            title: str,
            labels: List[str],
            values: List[float],
            description: str = "",
            y_axis_label: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a waterfall chart configuration.

        Args:
            title: Chart title
            labels: Category labels
            values: Values (positive for increase, negative for decrease)
            description: Optional description text
            y_axis_label: Label for Y-axis

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_waterfall_chart(
                title="Profit & Loss Statement",
                labels=["Revenue", "Cost of Goods", "Operating Expenses", "Taxes", "Net Profit"],
                values=[100000, -40000, -25000, -10000, 25000]
            )
        """
        try:
            if len(labels) != len(values):
                return {
                    "success": False,
                    "error": "labels and values must have the same length"
                }

            # Calculate cumulative values
            cumulative = 0
            waterfall_data = []

            for i, value in enumerate(values):
                if i == len(values) - 1:
                    # Last item is total
                    waterfall_data.append({
                        "value": cumulative + value,
                        "itemStyle": {"color": "#3498db"}
                    })
                else:
                    start = cumulative
                    cumulative += value
                    waterfall_data.append({
                        "value": abs(value),
                        "itemStyle": {
                            "color": "#2ecc71" if value >= 0 else "#e74c3c"
                        }
                    })

            # Create stack data for waterfall effect
            assist_data = []
            cumulative = 0
            for i, value in enumerate(values[:-1]):
                assist_data.append(cumulative)
                cumulative += value
            assist_data.append(0)  # Last bar starts from 0

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"}
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "3%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": labels
                },
                "yAxis": {
                    "type": "value",
                    "name": y_axis_label,
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": [
                    {
                        "name": "Assist",
                        "type": "bar",
                        "stack": "Total",
                        "itemStyle": {
                            "borderColor": "transparent",
                            "color": "transparent"
                        },
                        "emphasis": {
                            "itemStyle": {
                                "borderColor": "transparent",
                                "color": "transparent"
                            }
                        },
                        "data": assist_data
                    },
                    {
                        "name": "Value",
                        "type": "bar",
                        "stack": "Total",
                        "label": {
                            "show": True,
                            "position": "inside"
                        },
                        "data": waterfall_data
                    }
                ]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating waterfall chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_word_cloud",
        description="Generate a word cloud for visualizing text frequency data. Perfect for customer feedback keywords, support ticket topics, sentiment analysis, survey responses.",
        tags={"visualization", "charts", "echarts", "wordcloud", "text"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Word Cloud Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_word_cloud(
            title: str,
            words: List[Dict[str, Any]],
            description: str = "",
            shape: str = "circle",
            ctx: Context = None
    ) -> dict:
        """
        Generate a word cloud configuration.

        Args:
            title: Chart title
            words: List of word objects with format: [{"name": "word", "value": frequency}, ...]
            description: Optional description text
            shape: Shape of word cloud ("circle", "cardioid", "diamond", "square")

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_word_cloud(
                title="Customer Feedback Keywords",
                words=[
                    {"name": "excellent", "value": 120},
                    {"name": "responsive", "value": 95},
                    {"name": "helpful", "value": 85},
                    {"name": "slow", "value": 60},
                    {"name": "friendly", "value": 75}
                ],
                shape="circle"
            )
        """
        try:
            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "show": True,
                    "formatter": "{b}: {c}"
                },
                "series": [{
                    "type": "wordCloud",
                    "shape": shape,
                    "left": "center",
                    "top": "center",
                    "width": "90%",
                    "height": "80%",
                    "right": None,
                    "bottom": None,
                    "sizeRange": [12, 60],
                    "rotationRange": [-90, 90],
                    "rotationStep": 45,
                    "gridSize": 8,
                    "drawOutOfBound": False,
                    "layoutAnimation": True,
                    "textStyle": {
                        "fontFamily": "sans-serif",
                        "fontWeight": "bold",
                        "color": lambda: f"rgb({int(160 + 95 * (0.5 - 0.5))}, {int(160 + 95 * (0.5 - 0.5))}, {int(160 + 95 * (0.5 - 0.5))})"
                    },
                    "emphasis": {
                        "focus": "self",
                        "textStyle": {
                            "shadowBlur": 10,
                            "shadowColor": "#333"
                        }
                    },
                    "data": words
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating word cloud: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_stacked_bar_chart",
        description="Generate a stacked bar chart showing composition over categories. Perfect for ticket status by priority, sentiment by product, response times by category.",
        tags={"visualization", "charts", "echarts", "stacked", "bar"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Stacked Bar Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_stacked_bar_chart(
            title: str,
            categories: List[str],
            series_names: List[str],
            series_data: List[List[float]],
            x_axis_label: str = "",
            y_axis_label: str = "",
            description: str = "",
            horizontal: bool = False,
            show_percentages: bool = False,
            ctx: Context = None
    ) -> dict:
        """
        Generate a stacked bar chart configuration.

        Args:
            title: Chart title
            categories: Category labels
            series_names: Names of stacked segments
            series_data: Data for each segment
            x_axis_label: Label for X-axis
            y_axis_label: Label for Y-axis
            description: Optional description text
            horizontal: If True, creates horizontal stacked bars
            show_percentages: If True, show percentage labels

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_stacked_bar_chart(
                title="Support Tickets by Priority and Status",
                categories=["High", "Medium", "Low"],
                series_names=["Open", "In Progress", "Resolved"],
                series_data=[
                    [15, 25, 40],  # Open
                    [10, 30, 35],  # In Progress
                    [5, 45, 125]   # Resolved
                ]
            )
        """
        try:
            if len(series_names) != len(series_data):
                return {
                    "success": False,
                    "error": "series_names and series_data must have the same length"
                }

            default_colors = ["#e74c3c", "#f39c12", "#2ecc71", "#3498db", "#9b59b6", "#1abc9c"]

            series_config = []
            for idx, (name, data) in enumerate(zip(series_names, series_data)):
                series_item = {
                    "name": name,
                    "type": "bar",
                    "stack": "total",
                    "data": data,
                    "itemStyle": {
                        "color": default_colors[idx % len(default_colors)]
                    },
                    "emphasis": {
                        "focus": "series"
                    }
                }

                if show_percentages:
                    series_item["label"] = {
                        "show": True,
                        "position": "inside",
                        "formatter": "{c}"
                    }

                series_config.append(series_item)

            if horizontal:
                chart_config = {
                    "title": {
                        "text": title,
                        "left": "center",
                        "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                    },
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "legend": {
                        "data": series_names,
                        "top": "bottom"
                    },
                    "grid": {
                        "left": "3%",
                        "right": "4%",
                        "bottom": "12%",
                        "containLabel": True
                    },
                    "xAxis": {
                        "type": "value",
                        "name": x_axis_label
                    },
                    "yAxis": {
                        "type": "category",
                        "data": categories,
                        "name": y_axis_label
                    },
                    "series": series_config
                }
            else:
                chart_config = {
                    "title": {
                        "text": title,
                        "left": "center",
                        "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                    },
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "shadow"}
                    },
                    "legend": {
                        "data": series_names,
                        "top": "bottom"
                    },
                    "grid": {
                        "left": "3%",
                        "right": "4%",
                        "bottom": "12%",
                        "containLabel": True
                    },
                    "xAxis": {
                        "type": "category",
                        "data": categories,
                        "name": x_axis_label,
                        "nameLocation": "middle",
                        "nameGap": 30
                    },
                    "yAxis": {
                        "type": "value",
                        "name": y_axis_label,
                        "nameLocation": "middle",
                        "nameGap": 50
                    },
                    "series": series_config
                }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating stacked bar chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_timeline_chart",
        description="Generate a timeline/Gantt-style chart for showing events over time. Perfect for ticket lifecycle, case duration, response times, incident timelines.",
        tags={"visualization", "charts", "echarts", "timeline", "gantt"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Timeline Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_timeline_chart(
            title: str,
            categories: List[str],
            events: List[Dict[str, Any]],
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a timeline/Gantt chart configuration.

        Args:
            title: Chart title
            categories: Category labels (e.g., ticket IDs, case names)
            events: List of events with format:
                    [{"category": "Ticket-001", "start": 0, "end": 5, "name": "Investigation", "color": "#3498db"}, ...]
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_timeline_chart(
                title="Support Ticket Lifecycle",
                categories=["Ticket-001", "Ticket-002", "Ticket-003"],
                events=[
                    {"category": "Ticket-001", "start": 0, "end": 2, "name": "Open", "color": "#e74c3c"},
                    {"category": "Ticket-001", "start": 2, "end": 8, "name": "In Progress", "color": "#f39c12"},
                    {"category": "Ticket-001", "start": 8, "end": 10, "name": "Resolved", "color": "#2ecc71"},
                    {"category": "Ticket-002", "start": 1, "end": 3, "name": "Open", "color": "#e74c3c"},
                    {"category": "Ticket-002", "start": 3, "end": 12, "name": "In Progress", "color": "#f39c12"}
                ]
            )
        """
        try:
            # Map categories to indices
            category_map = {cat: idx for idx, cat in enumerate(categories)}

            # Transform events into bar data
            series_data = []
            for event in events:
                cat_idx = category_map.get(event["category"])
                if cat_idx is not None:
                    series_data.append({
                        "name": event.get("name", ""),
                        "value": [
                            cat_idx,
                            event["start"],
                            event["end"],
                            event["end"] - event["start"]
                        ],
                        "itemStyle": {
                            "color": event.get("color", "#3498db")
                        }
                    })

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "formatter": lambda params: f"{params['name']}<br/>Duration: {params['value'][3]} units"
                },
                "grid": {
                    "left": "15%",
                    "right": "10%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "value",
                    "name": "Time",
                    "nameLocation": "middle",
                    "nameGap": 30,
                    "min": 0
                },
                "yAxis": {
                    "type": "category",
                    "data": categories,
                    "inverse": True
                },
                "series": [{
                    "type": "custom",
                    "renderItem": lambda params, api: {
                        "type": "rect",
                        "shape": {
                            "x": api.coord([api.value(1), api.value(0)])[0],
                            "y": api.coord([api.value(1), api.value(0)])[1] - api.size([0, 1])[1] / 2,
                            "width": api.size([api.value(3), 0])[0],
                            "height": api.size([0, 1])[1] * 0.6
                        },
                        "style": api.style()
                    },
                    "encode": {
                        "x": [1, 2],
                        "y": 0
                    },
                    "data": series_data
                }]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating timeline chart: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_sentiment_gauge_grid",
        description="Generate a grid of gauge charts for showing multiple sentiment scores. Perfect for sentiment by product/category, NPS scores by segment, satisfaction ratings.",
        tags={"visualization", "charts", "echarts", "sentiment", "gauge", "grid"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Sentiment Gauge Grid Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_sentiment_gauge_grid(
            title: str,
            gauges: List[Dict[str, Any]],
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Generate a grid of gauge charts for sentiment/scores.

        Args:
            title: Chart title
            gauges: List of gauge configs: [{"name": "Product A", "value": 85, "max": 100}, ...]
            description: Optional description text

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_sentiment_gauge_grid(
                title="Customer Satisfaction by Product",
                gauges=[
                    {"name": "Product A", "value": 85},
                    {"name": "Product B", "value": 72},
                    {"name": "Product C", "value": 91},
                    {"name": "Product D", "value": 68}
                ]
            )
        """
        try:
            num_gauges = len(gauges)
            cols = min(3, num_gauges)  # Max 3 columns
            rows = (num_gauges + cols - 1) // cols

            series = []

            for idx, gauge_config in enumerate(gauges):
                row = idx // cols
                col = idx % cols

                # Calculate position
                gauge_width = 100 / cols
                gauge_height = 100 / rows
                center_x = gauge_width * col + gauge_width / 2
                center_y = gauge_height * row + gauge_height / 2

                value = gauge_config["value"]
                max_val = gauge_config.get("max", 100)

                # Color based on value percentage
                if value / max_val >= 0.8:
                    color = "#2ecc71"  # Green - Good
                elif value / max_val >= 0.6:
                    color = "#f39c12"  # Orange - Average
                else:
                    color = "#e74c3c"  # Red - Poor

                series.append({
                    "type": "gauge",
                    "center": [f"{center_x}%", f"{center_y}%"],
                    "radius": f"{min(gauge_width, gauge_height) * 0.4}%",
                    "min": 0,
                    "max": max_val,
                    "progress": {
                        "show": True,
                        "width": 10
                    },
                    "axisLine": {
                        "lineStyle": {
                            "width": 10
                        }
                    },
                    "axisTick": {
                        "show": False
                    },
                    "splitLine": {
                        "show": False
                    },
                    "axisLabel": {
                        "show": False
                    },
                    "detail": {
                        "valueAnimation": True,
                        "fontSize": 16,
                        "offsetCenter": [0, "80%"],
                        "formatter": f"{{value}}"
                    },
                    "title": {
                        "show": True,
                        "offsetCenter": [0, "-80%"],
                        "fontSize": 12,
                        "color": "#333"
                    },
                    "data": [{
                        "value": value,
                        "name": gauge_config["name"],
                        "itemStyle": {
                            "color": color
                        }
                    }]
                })

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "top": "2%",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "series": series
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating sentiment gauge grid: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool(
        name="generate_trend_comparison_chart",
        description="Generate a line chart with trend indicators and comparison. Perfect for tracking sentiment trends, ticket volume over time, response time improvements.",
        tags={"visualization", "charts", "echarts", "trend", "comparison"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Generate Trend Comparison Chart Configuration",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def generate_trend_comparison_chart(
            title: str,
            time_periods: List[str],
            current_period: List[float],
            previous_period: List[float],
            metric_name: str = "Metric",
            description: str = "",
            show_percentage_change: bool = True,
            ctx: Context = None
    ) -> dict:
        """
        Generate a trend comparison chart with previous period comparison.

        Args:
            title: Chart title
            time_periods: Time period labels
            current_period: Current period values
            previous_period: Previous period values for comparison
            metric_name: Name of the metric being tracked
            description: Optional description text
            show_percentage_change: Show percentage change annotations

        Returns:
            dict: Complete chart configuration ready for display_chart tool

        Example:
            generate_trend_comparison_chart(
                title="Customer Satisfaction Trend",
                time_periods=["Week 1", "Week 2", "Week 3", "Week 4"],
                current_period=[75, 78, 82, 85],
                previous_period=[70, 72, 75, 78],
                metric_name="Satisfaction Score"
            )
        """
        try:
            if len(time_periods) != len(current_period) or len(time_periods) != len(previous_period):
                return {
                    "success": False,
                    "error": "All arrays must have the same length"
                }

            # Calculate percentage change
            if show_percentage_change and len(current_period) > 0:
                start_change = ((current_period[0] - previous_period[0]) / previous_period[0] * 100) if previous_period[
                                                                                                            0] != 0 else 0
                end_change = ((current_period[-1] - previous_period[-1]) / previous_period[-1] * 100) if \
                previous_period[-1] != 0 else 0

                trend_text = f"↑ {end_change:+.1f}%" if end_change > 0 else f"↓ {end_change:+.1f}%"

            chart_config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "legend": {
                    "data": ["Current Period", "Previous Period"],
                    "top": "bottom"
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "12%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": time_periods,
                    "boundaryGap": False
                },
                "yAxis": {
                    "type": "value",
                    "name": metric_name,
                    "nameLocation": "middle",
                    "nameGap": 50
                },
                "series": [
                    {
                        "name": "Current Period",
                        "type": "line",
                        "data": current_period,
                        "smooth": True,
                        "lineStyle": {"width": 3, "color": "#3498db"},
                        "itemStyle": {"color": "#3498db"},
                        "areaStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "rgba(52, 152, 219, 0.3)"},
                                    {"offset": 1, "color": "rgba(52, 152, 219, 0.05)"}
                                ]
                            }
                        },
                        "markPoint": {
                            "data": [
                                {"type": "max", "name": "Max"},
                                {"type": "min", "name": "Min"}
                            ]
                        }
                    },
                    {
                        "name": "Previous Period",
                        "type": "line",
                        "data": previous_period,
                        "smooth": True,
                        "lineStyle": {"width": 2, "type": "dashed", "color": "#95a5a6"},
                        "itemStyle": {"color": "#95a5a6"}
                    }
                ]
            }

            result = {
                "success": True,
                "chart_type": "echarts",
                "title": title,
                "description": description,
                "config": chart_config
            }

            return _json_serialize(result)

        except Exception as e:
            logger.exception(f"Error generating trend comparison chart: {e}")
            return {"success": False, "error": str(e)}