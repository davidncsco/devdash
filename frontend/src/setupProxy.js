const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  const url = `${process.env.REACT_APP_API_URL}`
  app.use('/questions',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/start',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/startvirtual',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/end',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/endvirtual',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/score',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/user',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/reset',createProxyMiddleware({target: {url},changeOrigin: true,}));
  app.use('/rank',createProxyMiddleware({target: {url},changeOrigin: true,}));
};

