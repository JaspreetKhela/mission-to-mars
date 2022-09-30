# _____

# Import dependecies
# _____

# Import the Browser function from the splinter library for using Chrome as the scarping web browser
from splinter import Browser

# Import the BeautifulSoup library for scraping the HTML from a webpage
from bs4 import BeautifulSoup as soup

# Import the pandas library for facilitating ETL processes
import pandas as pd

# Import the datetime library for accessing date and time functions
import datetime as dt

# Import the ChromeDriverManager function from the splinter library for using Chrome as the scarping web browser
from webdriver_manager.chrome import ChromeDriverManager

# _____

# Function Definitions
# _____

# Define a function for scraping a webpage
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Retrive the news title and paragraphs information from the scaped webpage
    news_title, news_paragraph = mars_news(browser)

    # Define the list of dictionaries containing hemisphere images and titles
    hemisphere_list = mars_hemisphere_data(browser)

    # Store the scraped data in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_data": hemisphere_list
        }

    # Stop webdriver and return data
    browser.quit()
    return data

# Define the mars news data collection function
def mars_news(browser):
    # Scrape Mars News by visiting the mars NASA news site
    # Define the URL to visit
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'

    # Visit the URL defined above
    browser.visit(url)

    # Optional delay for loading the page so that the targeted HTML elements have time to load
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser HTML to a BeautifulSoup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find a div tag with the list_text class attribute value
        slide_element = news_soup.select_one('div.list_text')

        # Use the parent element to find the first anchor tag and save it as news_title
        news_title = slide_element.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_paragraph = slide_element.find('div', class_='article_teaser_body').get_text()

    # Account for AttributeErrors
    except AttributeError:
        return None, None

    return news_title, news_paragraph

# Define the feature image data collection function
def featured_image(browser):
    # Define a URL to visit
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    
    # Visit the URL above
    browser.visit(url)

    # Find and click on the full image button
    full_image_element = browser.find_by_tag('button')[1]
    full_image_element.click()

    # Store and parse the resulting HTML using BeautifulSoup
    html = browser.html
    image_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image URL
        image_url_relative = image_soup.find('img', class_='fancybox-image').get('src')

    # Account for AttributeErrors
    except AttributeError:
        return None

    # Use the base URL of the webpage to create an absolute URL for an image
    image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{image_url_relative}'

    # Return the image's absolute URL
    return image_url

# Define the mars facts data collection function
def mars_facts():
    # Add try/except for error handling
    try:
        # Use read_html to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    # Account for BaseExceptionErrors
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into an HTML table and add Bootstrap
    return df.to_html(classes="table table-striped")

# Define the mars hemisphere data collection function
def mars_hemisphere_data(browser):
    # 1.1. Use the browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 1.2. Create a list to hold the images and titles
    hemisphere_image_urls = []
    hemisphere_titles = []
    hemisphere_list = []

    # 1.3. Write code to retrieve the image urls and titles for each hemisphere
    # Find an anchor tag with the class attribute value of product-item
    links = browser.find_by_css('a.product-item img')
    
    # Loop through the links list
    for i in range(len(links)):
        # Define a hemisphere dictionary to store an image's URL and title
        hemisphere = {}

        # Find an anchor tag with a class attribute value of product-item
        browser.find_by_css('a.product-item img')[i].click()

        # Store and parse the resulting HTML using BeautifulSoup
        html = browser.html
        image_soup = soup(html, 'html.parser')

        # Find the relative URL of an image tag with a class of wide-image
        image_url_relative = image_soup.find('img', class_='wide-image').get('src')

        # Create an absolute URL using the relative image URL above
        image_url = f'https://marshemispheres.com/{image_url_relative}'

        # Find an h2 tag with a class attribute value of title
        title = image_soup.find('h2', class_='title').get_text()
        
        # Add the image URL to a list and a dictionary 
        hemisphere_image_urls.append(image_url)
        hemisphere["image_url"]=image_url

        # Add the titles to a list and a dictionary
        hemisphere_titles.append(title)
        hemisphere["title"]=title

        # Add the hemisphere dictionary to a list
        hemisphere_list.append(hemisphere)
        browser.back()

    # Return the list of hemisphere dictionaries
    return hemisphere_list

# If this script is run directly, run the following code
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())