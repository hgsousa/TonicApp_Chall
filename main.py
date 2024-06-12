from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import openai


openai.api_key = 'openai_api_key'


def fetch_articles(url):
    response = requests.get(url)
    print(response.status_code)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        #print(soup)

        # Find all article elements in website
        all_articles = soup.find_all('div', class_='css-8atqhb')

        print(all_articles)

        articles_list = []

        for article in all_articles:
            article_title_tag = article.find('h2').get_text(strip=True)
            article_url_tag = article.select_one('a')['href']
            article_date_tag = article.select_one('div').get_text(strip=True)

            #print(article_title_tag, article_url_tag, article_date_tag)

            #verify if the articles were posted in the last 7 days
            date = datetime.strptime(article_date_tag, '%B %d, %Y')
            print(article_date_tag, date)

            if datetime.now() - date < timedelta(days=7):
                articles_list.append({
                    'title': article_title_tag,
                    'link': article_url_tag,
                    'date': article_date_tag
                })

        articles_3_list = sorted(articles_list, key=lambda x: datetime.strptime(x['date'], '%B %d, %Y'), reverse=True)

        x = articles_3_list[-3:]

        return x

def generate_wrap_up(articles):
    i = 0
    articles_analyse_list = []

    def analyze_content(content):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in medical articles."},
                {"role": "user",
                 "content": f"Analyze the following medical article content and identify positive and negative trends:\n\n{content}"}
            ]
        )
        analysis = response['choices'][0]['message']['content']
        # Format the analysis text with HTML tags
        formatted_analysis = analysis.replace('\n', '<br>')

        return formatted_analysis


    for article in articles:
        response = requests.get(article['link'])
        soup = BeautifulSoup(response.content, 'html.parser')
        article_content = soup.find('article').get_text()

        print("article N:",i, article_content)
        i += 1

        analysis = analyze_content(article_content)


        articles_analyse_list.append({
            'title': article['title'],
            'link': article['link'],
            'date': article['date'],
            'analyse': analysis
        })

        print(articles_analyse_list)

    return articles_analyse_list


def create_newsletter(articles_analyse_list):
    article_template = """
    <div class="article">
        <h2 class="article-title">{title}</h2>
        <p class="article-date">{date}</p>
        <a class="article-link" href="{link}" target="_blank">Read full article</a>
        <div class="analysis">
            <h3>Analysis:</h3>
            <p>{analyse}</p>
        </div>
    </div>
    """

    articles_html = ""
    for article in articles_analyse_list:
        articles_html += article_template.format(
            title=article['title'],
            date=article['date'],
            link=article['link'],
            analyse=article['analyse']
        )

    tonic_app_news = """
        <div class="tonic-app-news">
            <h2>Tonic App News</h2>
            <p>For new features, visit <a href="https://tonicapp.io/" target="_blank">Tonic App</a>.</p>
        </div>
        """


    with open("template.html", "r") as file:
        template = file.read()

    newsletter_content = template.replace("{articles}", articles_html + tonic_app_news)

    with open("weekly_healthcare_news.html", "w") as file:
        file.write(newsletter_content)

    return newsletter_content


if __name__ == "__main__":

    # URL of the healthcare website to scrape articles
    url = "https://www.medicalnewstoday.com/news"

    articles_list = fetch_articles(url)

    articles_analyse_list = generate_wrap_up(articles_list)
    newsletter_content = create_newsletter(articles_analyse_list)

    print("--- Done ---")


