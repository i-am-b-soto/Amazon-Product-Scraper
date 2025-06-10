class AmazonProduct:
    _title = None
    _price = None
    _description = None
    _url = None

    def __init__(self, title="N/A", price="N/A", description=None, url=None):
        self._title = title
        self._price = price
        self._description = description
        self._url = AmazonProduct.fix_url(url)

    @staticmethod
    def fix_url(url):
        ref_index = url.find('/ref=')
        if ref_index != -1:
            url = url[:ref_index]

        return url        

    def to_json(self):
        return {"Title": self._title, "Price": self._price, 
                "Description": self._description, "url": self._url}