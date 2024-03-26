/* 
 * viewer-request handler responding to POST requests with an immediate
 * 204 No Content (rather than the service default of 403 Forbidden).
 *
 * THIS IS NECESSARY TO SUPPORT THE UPLOAD BANDWIDTH TEST.
 *
 * The CDN is otherwise a static file server, which does not support
 * POST requests. POSTs *may* be forwarded back to the file origin (S3),
 * affecting the nature of the error response; but, the result is the
 * same.
 *
 * While most current browsers are *not* concerned by this error
 * response, and the test proceeds without issue, *some* browsers
 * (cough cough Safari) are affected, in a manner which yields bizarre
 * – and false – results.
 *
 * Regardless, it is undesirable that the speed test server respond to
 * upload test requests with an error.
 *
 * Note: The below handler does not concern itself with the request path
 * – rather, only the request method (POST). It is the responsibility of
 * the CDN configuration to apply this handler to the correct path (in
 * the parlance of CloudFront to the correct "behavior").
 *
 */
function handler (event) {
  const request = event.request;

  if (request.method == 'POST') {
    return {
        statusCode: 204,
        statusDescription: 'No Content'
    };
  }

  return request;
}
