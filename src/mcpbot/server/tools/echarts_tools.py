from mcp import types
from fastmcp import Context
import logging
import json
from .tool_logger import ToolLogger
from typing import List, Dict, Any, Literal, Optional

################################
# Configuration and Initialization
################################

logger = logging.getLogger(__name__)


################################
# Helper Functions
################################

def _json_serialize(obj):
    """Helper function to ensure proper JSON serialization."""
    return json.loads(json.dumps(obj))


################################
# ECharts Tool Registrations
################################

def register_echarts_tools(mcp):
    @mcp.tool(
        name="display_chart",
        description="Display an interactive Apache ECharts chart in the chat interface. Supports line charts, bar charts, pie charts, scatter plots, and more. Returns a chart configuration that will be rendered in the UI.",
        tags={"visualization", "charts", "echarts"},
        meta={"version": "1.0", "author": "support-team"},
        annotations=types.ToolAnnotations(
            title="Display ECharts Visualization",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def display_chart(
            chart_config: dict,
            title: str = "Chart",
            description: str = "",
            ctx: Context = None
    ) -> dict:
        """
        Display an Apache ECharts chart in the chat interface.

        Args:
            chart_config: ECharts option configuration object (dict)
            title: Title to display above the chart
            description: Optional description text below the title
            ctx: FastMCP context

        Returns:
            dict: Success/error status with chart data

        Example chart_config for a simple line chart:
        {
            "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
            "yAxis": {"type": "value"},
            "series": [{"data": [120, 200, 150, 80, 70], "type": "line"}]
        }
        """
        try:
            # Validate that chart_config is a dict
            if not isinstance(chart_config, dict):
                return {
                    "success": False,
                    "error": "chart_config must be a dictionary"
                }

            # Return the chart data to be sent to the client
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
            logger.exception(f"Error creating chart: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool(
        name="generate_line_chart",
        description="Generate a line chart configuration for displaying trends over time or categories. Perfect for showing temperature trends, stock prices, sales over time, etc.",
        tags={"visualization", "generate", "charts", "echarts", "line"},
        meta={"version": "1.0", "author": "martin"},
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
            await ToolLogger.log_to_client(
                ctx,
                f"Generating line chart configuration...",
                "info"
            )
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
        tags={"visualization", "generate", "charts", "echarts", "bar"},
        meta={"version": "1.0", "author": "martin"},
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
            await ToolLogger.log_to_client(
                ctx,
                f"Generating bar chart configuration...",
                "info"
            )
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
        tags={"visualization", "generate", "charts", "echarts", "pie"},
        meta={"version": "1.0", "author": "martin"},
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
            await ToolLogger.log_to_client(
                ctx,
                f"Generating pie chart configuration...",
                "info"
            )
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
        tags={"visualization", "generate", "charts", "echarts", "scatter"},
        meta={"version": "1.0", "author": "martin"},
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
            await ToolLogger.log_to_client(
                ctx,
                f"Generating scatter plot configuration...",
                "info"
            )
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
        tags={"visualization", "generate", "charts", "echarts", "multi-series"},
        meta={"version": "1.0", "author": "martin"},
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
            await ToolLogger.log_to_client(
                ctx,
                f"Generating multi-series chart configuration...",
                "info"
            )
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