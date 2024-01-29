import React, { useState, useEffect } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link
} from 'react-router-dom';
import { Container, List, ListItem } from '@mui/material';

import HerbDetail from './HerbDetail';
import './App.css'

const App = () => {
  return (
      <Router>
        <Container>
          <div className="App">
            <h1>Chinese Herbs</h1>
              <TSVParser />
          </div>
        </Container>
      </Router>
  );
}

const TSVParser = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/herbs.tsv')
        .then(response => response.text())
        .then(tsvString => {
          const parsedData = parseTSV(tsvString);
          setData(parsedData);
        })
        .catch(error => console.error('Error fetching TSV:', error));
  }, []);

  console.log("data", data)
  return (
    <List>
      {data.map((herb) => {
        const name = getHerbDisplayName(herb);
        return (
          <ListItem key={name}>
            <Link to={`/herb/${name}`}>{name}</Link>
          </ListItem>
        );
      })}
      <Routes>
        {data.map((herb) => {
          const name = getHerbDisplayName(herb);
          return (
            <Route key={name} path={`/herb/${name}`} element={<HerbDetail herb={herb} />} />
          );
        })}
      </Routes>
    </List>
  );
};

const getHerbDisplayName = (herb) => {
    return herb["English Name"]?.split(",")[0];
}

const parseTSV = (tsvString) => {
  const lines = tsvString.split('\n');
  const header = lines[0].split('\t');
  return lines.slice(1).map(line => {
    const data = line.split('\t');
    return header.reduce((obj, nextKey, index) => {
      obj[nextKey] = data[index];
      return obj;
    }, {});
  });
};

export default App;
