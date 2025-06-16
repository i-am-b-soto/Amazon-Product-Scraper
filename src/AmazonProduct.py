class AmazonProduct:
    _title = None
    _ASIN = None
    _stars = None
    _review_count = None
    _image = None
    _price = None
    _description = None
    _url = None

    def __init__(self, title="N/A", price="N/A", description=None, url=None,
                 image=None, ASIN="N/A", stars=None, review_count=None):
        self._title = title
        self._price = price
        
        if description is not None:
            self._description = description[:1024]
        else:
            pass

        self._url = AmazonProduct.fix_url(url)
        self._image = image
        self._ASIN = ASIN
        self._stars = stars
        self._review_count = review_count

    @staticmethod
    def fix_url(url):
        ref_index = url.find('/ref=')
        if ref_index != -1:
            url = url[:ref_index]

        return url        

    def to_dict(self):
        return {
                "ASIN": self._ASIN,
                "Title": self._title,
                "Price": self._price, 
                "Stars": self._stars,
                "Review Count": self._review_count, 
                "Image": self._image,
                "Description": self._description, 
                "URL": self._url
                }