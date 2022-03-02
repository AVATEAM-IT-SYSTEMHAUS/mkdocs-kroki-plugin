from bs4 import BeautifulSoup
from functools import partial
from mkdocs.plugins import log


info = partial(log.info, 'KROKI %s')
debug = partial(log.debug, 'KROKI %s')
error = partial(log.error, 'KROKI %s')


tag_blocklist = ('script')


def _sanitize_svg(svg_soup):
    for tag in svg_soup.findAll():
        is_blocked = tag.name.lower() in tag_blocklist
        conatins_external_refs = 'http' in tag.text.lower()
        if is_blocked or conatins_external_refs:
            tag.extract()
            continue

        for attr in tag.attrs:
            is_script_function = attr.lower().startswith('on')
            has_external_refs = 'http' in ''.join(tag.attrs[attr]).lower()
            if any([is_script_function, has_external_refs]):
                tag.attrs.remove(attr)


def clean_svg(svg_data):
    svg_soup = BeautifulSoup(svg_data, 'html.parser')

    # suppress upscaling of smaller images
    if 'width' in svg_soup.svg.attrs:
        max_width = svg_soup.svg.attrs['width']
        svg_soup.svg.attrs['style'] = f'max-width: {max_width}'

    # set the viewbox if not present
    if 'viewbox' not in svg_soup.svg.attrs:
        if ('height' in svg_soup.svg.attrs) \
          and ('width' in svg_soup.svg.attrs):
            height = ''.join(filter(str.isdigit, svg_soup.svg.attrs['height']))
            width = ''.join(filter(str.isdigit, svg_soup.svg.attrs['width']))
            svg_soup.svg.attrs['viewbox'] = f'0 0 {width} {height}'
        else:
            error('SVG does not contain viewbox or height and width.')

    # remove unnecessary attrs
    svg_soup.svg.attrs = {k: v for k, v in svg_soup.svg.attrs.items()
                          if k in ['version', 'viewbox', 'style']}

    _sanitize_svg(svg_soup)

    return svg_soup.svg
