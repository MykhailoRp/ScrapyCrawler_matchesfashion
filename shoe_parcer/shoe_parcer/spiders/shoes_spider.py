import scrapy

def get_gender(url):
    if '/mens/' in url: return 'male'
    elif '/womens/' in url: return 'female'
    else: return 'unknown'

class ShoesSpider(scrapy.Spider):
    name = "shoes"

    start_urls = [
        "https://www.matchesfashion.com/womens/shop/shoes",
        "https://www.matchesfashion.com/mens/shop/shoes",
    ]

    def parse(self, response):

        products = response.xpath('//div[@data-testid="ProductCard-productCard"]')

        first_product = ":".join(products[0].xpath('.//a/div//p/text()').getall())

        for product in products[1:]:

            product_title = ":".join(product.xpath('.//a/div//p/text()').getall())

            price_drop = product.xpath('normalize-space(.//span[@data-testid="ProductPrice-rrp"])').get()

            if price_drop is None:
                price_full = product.xpath('.//span[@data-testid="ProductPrice-billing-price"]/text()').get()
            else:
                price_full = price_drop.replace('(', '').replace(')', '')
                price_drop = product.xpath('.//span[@data-testid="ProductPrice-billing-price"]/text()').get()

            product_url = product.xpath('.//a[@data-testid="ProductCard-link"]/@href').get()

            yield scrapy.Request(
                url=response.urljoin(product_url),
                callback=self.parse_product_details,
                meta={
                    'title': product_title,
                    'url': response.urljoin(product_url),
                    'price_full': price_full,
                    'price_drop': price_drop,
                    'gender': get_gender(response.url)
                }
            )

            if product_title == first_product: break

        next_page = response.xpath('//a[@data-testid="SearchResults-loadMore"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_product_details(self, response):

        yield {
            'title': response.meta['title'],
            'url': response.meta['url'],
            'price_full': response.meta['price_full'],
            'price_drop': response.meta['price_drop'],
            'image_url': response.urljoin(response.xpath('//img[@class="iiz__img "]/@src').get()),
            'category': set(response.xpath('//a[@data-testid="ViewAllPills-related-category-link"]/text()').getall()),
            'gender': response.meta['gender']
        }