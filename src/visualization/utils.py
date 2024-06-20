def add_code(html_page_path="./html/team_page.html", plot_code=""):
    
    with open(html_page_path, "r") as html_page:
        html_page_code = html_page.read()
    
    html_page_split = html_page_code.split('<div id="plot">')
    new_html_code = html_page_split[0] + plot_code + html_page_split[1]
    return new_html_code