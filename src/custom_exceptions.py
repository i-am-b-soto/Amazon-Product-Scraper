class ProductListPageNotLoaded(Exception):
    def __init__(self, message):            
        super().__init__(message)


class ProductNotLoaded(Exception):
    def __init__(self, message):            
        super().__init__(message)