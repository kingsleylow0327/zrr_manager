def expriy_date_parse(date):
    ret_date = "2 week"
    if date == "1m":
        ret_date = "1 month"
    elif date == "3m":
        ret_date = "3 month"
    elif date == "6m":
        ret_date = "6 month"
    
    return ret_date