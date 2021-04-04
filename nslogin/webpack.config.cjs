const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const IgnoreEmitPlugin = require("ignore-emit-webpack-plugin");

module.exports = {
  // mode: 'development',
  entry: {
    'login': './src/login.js',
    '403': './src/403.js',
    'change-password': './src/change-password.js',
    'post-login': './src/post-login.js',
    'register': './src/register.js',
    'css': './src/style.scss'
  },
  devtool: 'source-map',
  output: {
    filename: 'static/js/[name].js',
    path: path.resolve(__dirname),
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'static/css/style.css'
    }),
    new IgnoreEmitPlugin([/css\.js/]),
    new HtmlWebpackPlugin({
      filename: 'templates/login.template.html',
      template: 'src/login.template.html',
      inject: false
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/403.template.html',
      template: 'src/403.template.html',
      inject: false
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/post-login.template.html',
      template: 'src/post-login.template.html',
      inject: false
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/change-password.template.html',
      template: 'src/change-password.template.html',
      inject: false
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/register.template.html',
      template: 'src/register.template.html',
      inject: false
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
