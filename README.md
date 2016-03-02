# Search Engine Quality Evaluation

##Preparation

Please replace the 'PLACEHOLDER's at the top of searchquality.py before running the script.

### How to get a Google API key
1. Go to https://console.developers.google.com/
2. Create a new project
3. Enable APIs if you want (optional; Custom Search API is enabled by default on a new project.)
4. Go to [Credentials] page
5. Click [Create credentials] and select [API key]
6. Select [Server key]

### How to get a Google Search engine ID
1. Go to https://cse.google.com/cse/all
2. Create a new search engine
3. Type any site to 'Sites to search' box (e.g. www.example.com)
You cannot leave this box blank, but the value can be removed later.
4. Type a search engine name (e.g. entireweb) and click [CREATE]
5. Click 'Control Panel'
6. You will see the item you added at step 3. in the 'Sites to search' section. Now you can delete it.
7. 'Sites to search' section has a dropdown list and its default value should be 'Search only included sites'.
Change this to 'Search the entire web but emphasize included sites'.
8. You can get a Search engine ID by clicking the [Search engine ID] button in the 'Details' section.

### How to enable Bing Search API and get an Azure account key
1. Go to https://datamarket.azure.com/dataset/bing/search
2. Sign up a free plan or buy a subscription
3. Go to [My Account] tab and check [Primary Account Key]
4. Uncheck 'I agree that Microsoft may use my email address to provide ...' if you want.
