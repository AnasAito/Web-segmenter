# Web-segmenter : An Advanced HTML Parser for Efficient Content Structuring and Search

Parsing HTML content is a common task in web development.the output is usualy strutred when we are familiar witth the website template. But sometimes no website template is available.
So we usually pars ethe raw htmland try to male sense of it afterusing complex NlP piplines. 

With websegmenter,Look no further! Web segmenter uses the HTML layout to automatically structure the content into meaningful segments, 
allowing for quick and easy navigation and search. And the best part? It all happens in ``under a second``, so you can get back to focusing on what matters most.


## Key Features

- Automatic segmentation of content into meaningful sections based on the HTML layout
- Advanced search functionality for finding specific content within seconds


## Usage

Using our HTML parser is simple and straightforward. Here's an example of how you can use it to structure and search through HTML content:

```python
from utils import WebSegmenter

# Parse HTML content
websegmenter = WebSegmenter(url='https://www.dataiku.com/')
websegmenter.run()

# Access segmented content
segments = websegmenter.ranked_nodes()
print(segments)
# (5) Results
# [('9de8bb0c61e4ae7106bb5013b5c976f26e87f172',
#   {'item_class': 'other',
#    'label': 'Products',
#    'score': 49,
#    'to_filter': False}),
#  ('01f0f02546c961522bc83e26fa4980ac0b5e3ade',
#   {'item_class': 'other',
#    'label': 'Products',
#    'score': 30,
#    'to_filter': False}),
#  ('f2bd7dec18353fc981bba32520134ca49b6f3c2b',
#   {'item_class': 'links_list',
#    'label': 'Products',
#    'score': 11,
#    'to_filter': False}),
#  ('a96eb033a46084cedf05fdd66ff105e4d8adca34',
#   {'item_class': 'is_paragraph',
#    'label': 'â\x80\x9cThe Chrome extension is the hero of the product '
#             'itself.â\x80\x9d',
#    'score': 2,
#    'to_filter': False}),
#  ('cfe00fc25e6c3cdf2b193c153303db08aae8622b',
#   {'item_class': 'is_paragraph',
#    'label': 'â\x80\x9cThe Chrome extension is the hero of the product '
#             'itself.â\x80\x9d',
#    'score': 2,
#    'to_filter': False})]

# Search for specific content
results = parser.search("product")
print(results)
# {'id': '9de8bb0c61e4ae7106bb5013b5c976f26e87f172',
#  'content': [{'type': 'atom', 'payload': 'Products', 'index': 8},
#              {'type': 'atom', 'payload': 'Customers', 'index': 9},
#              {'type': 'atom', 'payload': 'Company', 'index': 10},
#              {'type': 'atom', 'payload': 'Social', 'index': 11},
#              {'type': 'atom', 'payload': 'Policies', 'index': 12}],
#  'links': [
#            {'href': '/products/buyer-intent-data',
#             'text_payload': ['Buyer Intent Data']},
#            {'href': '/products/pitch-intelligence',
#             'text_payload': ['Pitch Intelligence']},
#            {'href': 'https://www.instagram.com/seamless.ai/',
#             'text_payload': ['Instagram']},
#            {'href': '/products/autopilot', 'text_payload': ['Autopilot']},
#            {'href': '/customers/presidents-club/presidents-club-winners',
#             'text_payload': ['Case Studies']},
#            {'href': '/cookies', 'text_payload': ['Cookies']},
#            {'href': 'https://www.facebook.com/SeamlessAI/',
#             'text_payload': ['Facebook']},
#            {'href': '/customers/get-support', 'text_payload': ['Get Support']},
#            {'href': '/pricing', 'text_payload': ['Pricing']},
#            {'href': 'https://www.tiktok.com/@seamless.ai',
#             'text_payload': ['TikTok']},
#            {'href': '/policies?tab=policies-termsofuse',
#             'text_payload': ['Terms of Use']},
#            {'href': '/company/contact-us', 'text_payload': ['Contact Us']},
#            {'href': '/products/chrome-extension',
#             'text_payload': ['Chrome Extension']},
#            {'href': '/company/about-us', 'text_payload': ['About Us']},
#            {'href': 'https://www.seamless.ai/directory/c-a',
#             'text_payload': ['Directory']},
#            {'href': '/products/platform-overview',
#             'text_payload': ['Platform Overview']},
#            {'href': 'https://www.linkedin.com/company/3184655/',
#             'text_payload': ['Linkedin']},
#       ...]}

# get content
node_id ,node_meta= results[0]
node_summary = websegmenter.summarize(node_id=node_id)
print(node_summary,sort_dicts=False)

```
# Advance search
sometimes websites dont use specific keywords to reference content for example Product could be features ...
for this we present ``advance search functionality``.

Go beyound simple keyword search, use links to find specific parents. you can also use the item classifier to filter content (item with a grid of elements , item with a list of links only or simply a pragraph)
```python
websegmenter = WebSegmenter(url='https://www.dataiku.com/')
websegmenter.run()
results = websegmenter.search(keyword = 'product',
                              advance_search = {
                                'item_class_in' : ['links_list'],
                                'search_in_links' : True
                              }
                              )
# results = websegmenter.search('product')
print(f'({len(results)}) Results')
pprint.pprint(results)
print('--------------------')
print('First result summary')
print('--------------------')
try : 
    node_id = results[0][0]
    node_summary = websegmenter.summarize(node_id=node_id)
    pprint.pprint(node_summary,sort_dicts=False)
except : 
    print('No results found ...')
# (6) Results
# [('85ab699e1cb5be8e79ad4141edd54243a7356b75',
#   {'item_class': 'links_list',
#    'label': 'Data Preparation',
#    'score': 7,
#    'to_filter': False}),
#  ('cc62b005d3ae971d62e743acc3e873f492b1c39f',
#   {'item_class': 'links_list',
#    'label': 'Collaboration',
#    'score': 7,
#    'to_filter': False}),
#  ('4cadb439c2c93f1bafd585a0b1e4710c3abc50fb',
#   {'item_class': 'links_list',
#    'label': 'AI and Us',
#    'score': 7,
#    'to_filter': False}),
#  ('0f340b8d76de9538ac40ee4f47cb5270042968be',
#   {'item_class': 'links_list',
#    'label': 'Watch a Demo of Dataiku',
#    'score': 5,
#    'to_filter': False}),
#  ('7bb54eed0b23b10c291746c67d21017aae8b2772',
#   {'item_class': 'links_list',
#    'label': 'Everyday AI, Extraordinary People',
#    'score': 4,
#    'to_filter': False}),
#  ('e15a4858eb3be10bad574a7646e5af324bf410fb',
#   {'item_class': 'links_list',
#    'label': 'Watch a Demo of Dataiku',
#    'score': 3,
#    'to_filter': False})]
# --------------------
# First result summary
# --------------------
# {'id': '85ab699e1cb5be8e79ad4141edd54243a7356b75',
#  'content': [{'type': 'atom', 'payload': 'A Single Platform For', 'index': 18}],
#  'links': [{'href': 'https://www.dataiku.com/product/key-capabilities/mlops/',
#             'text_payload': ['MLOps']},
#            {'href': 'https://www.dataiku.com/product/key-capabilities/data-visualization/',
#             'text_payload': ['Visualization']},
#            {'href': 'https://www.dataiku.com/product/key-capabilities/dataops/',
#             'text_payload': ['DataOps']},
#            {'href': 'https://www.dataiku.com/product/key-capabilities/analytic-apps/',
#             'text_payload': ['Analytic Apps']},
#            {'href': 'https://www.dataiku.com/product/key-capabilities/data-preparation/',
#             'text_payload': ['Data Preparation']},
#            {'href': 'https://www.dataiku.com/product/key-capabilities/machine-learning/',
#             'text_payload': ['Machine Learning']}]}
```

# Contributions
We welcome contributions from the community to help improve and enhance our HTML parser. Whether you find a bug, have a feature request, or would like to contribute to the codebase, we'd love to hear from you. Simply fork our repository, make your changes, and submit a pull request - it's that easy!




