import os.path
import numpy as np
import jinja2
# from .lib_cluster_maker import color_gradient, set_color_on_background

ROOT_FOLDER = os.path.dirname(os.path.dirname(__file__))

def build_table_html(
        assets,
        class_id_vars,
        title, # UNUSED
        template_path, # UNUSED
        output_path,
        assessment_type, # UNUSED
        weights = None,
    ):
    data = assets.loc[:, class_id_vars[1:]]
    print(class_id_vars)
    print(data.columns)
    if weights is None:
        weights = [1/(len(data.columns) - 2)] * len(data.columns)
    data_weights = list(zip(data.columns[1:-1], weights))
    data_weights.append((data.columns[-1], 1))
    data_info = [(
            indicator,
            weight,
            f"{data.loc[:, indicator].mean():.4f}",
            f"{data.loc[:, indicator].std():.4f}"
        ) for indicator, weight in data_weights]
    data_columns = data.columns[1:]
    print(data_info)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("res/templates"),
        #autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("template-assets.html")
    html_page = template.render(data=data, data_info=data_info, data_columns=data_columns, root_folder=ROOT_FOLDER)
    with open(output_path, 'w') as f:
        f.write(html_page)
    return html_page
