const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: [
    './src/login.js',
    './src/style.scss'
  ],
  devtool: 'source-map',
  output: {
    filename: 'static/js/login.js',
    path: path.resolve(__dirname),
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'static/css/style.css'
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/login.template.html',
      template: 'src/login.template.html',
      inject: false,
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/403.html',
      template: 'src/403.html',
      inject: false,
    }),
  ],
  module: {
    rules: [
      {
        test: /\.s[ac]ss$/i,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'],
      },
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        resolve: {
          fullySpecified: false,
        },
        use: {
          loader: 'babel-loader',
        },
      },
    ],
  },
};
