/*
 * viewer-request event handler to redirect requests for a `www.DO.MAIN`
 * host to the `DO.MAIN` host.
 *
 * I.e. this handler strips the `www.` prefix from the domain.
 *
 */
function handler (event) {
    const host = event.request.headers.host.value;
    
    if (host.startsWith('www.')) {
        const newHost = host.slice(4);
        
        const qstr = encodeRequestQuery(event.request.querystring);
        const qpart = qstr === '' ? '' : `?${qstr}`;
        
        const location = `https://${newHost}${event.request.uri}${qpart}`;
        
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {
                location: {value: location}
            }
        };
    }
    
    return event.request;
}

/*
 * Patches lack of
 * https://developer.mozilla.org/en-US/docs/Web/API/Location/search in event.
 *
 * Inspired by
 * https://github.com/aws-samples/amazon-cloudfront-functions/issues/11.
 *
 * @param {import("aws-lambda"). CloudFrontFunctionsQuerystring} querystring The weird format exposed by CloudFront
 * https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/functions-event-structure.html#functions-event-structure-query-header-cookie
 *
 * @returns {string} Tries to return the same as
 * https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams/toString
 *
 */
function encodeRequestQuery (querystring) {
    const parts = [];

    for (const param in querystring) {
        const query = querystring[param];
        
        if (query.multiValue) {
            parts.push(query.multiValue.map((item) => param + '=' + item.value).join('&'));
        } else if (query.value === '') {
            parts.push(param);
        } else {
            parts.push(param + '=' + query.value);
        }
    }

    return parts.join('&');
}
