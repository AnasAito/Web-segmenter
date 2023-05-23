# %%
from utils import WebSegmenter,visualize_graph,get_summary
import pprint

# %%
# websegmenter = WebSegmenter(url='https://www.dataiku.com/')
websegmenter = WebSegmenter(url='https://kumo.ai/')
websegmenter.run()
# %%
