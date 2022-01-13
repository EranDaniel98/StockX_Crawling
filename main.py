from stockX_crawler import StockX_crawler
import threading


def main():
    crawl = StockX_crawler()

    file_lines_count = crawl.get_file_lines_count('shoes_url_list.txt')

    if(file_lines_count == 0):  # If there are no shoes links in 'shoes_link_url.txt'
        crawl.brands_urls = crawl.get_brand_urls()  # crawl for shoes links

        for url in crawl.brands_urls:
            print('\n' + url)
            crawl.create_shoes_urls_file(url)

    file_lines_count = crawl.get_file_lines_count(
        'shoes_url_list.txt')  # get shoes link len

    while(file_lines_count != 0):
        crawl.get_shoes_data()
        file_lines_count = crawl.get_file_lines_count('shoes_url_list.txt')

        print('Finished 5 shoes')

    print('FINISHED')


if __name__ == "__main__":
    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=main)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    #main()
