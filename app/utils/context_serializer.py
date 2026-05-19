def serialize_business_context(context):

    return {
        "industry": context.industry,
        "ideal_customer": context.ideal_customer,
        "product": context.product,
    }
