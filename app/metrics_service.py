def build_category_chart_data(category_metrics):
    return {
        "Categoría": [row[0] for row in category_metrics],
        "Total": [row[1] for row in category_metrics]
    }