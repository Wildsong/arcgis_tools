import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { AppSettings } from './appSettings'

const apiServer = AppSettings.SERVER;

const root = ReactDOM.createRoot(document.getElementById('app'));
root.render(
  <>
    <App title="Clatsop County Records" />
  </>
);
