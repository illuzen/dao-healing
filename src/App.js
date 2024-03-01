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
        .catch(error => console.error('Error fetching CSV:', error));
  }, []);

  console.log("data", data)
  return (
      <Routes>
          {data.map((herb) => {
              const name = getHerbDisplayName(herb);
              return (
                  <Route key={name} path={`/herb/${name}`} element={<HerbDetail herb={herb} />} />
              );
          })}
          <Route key={'home'} path={`/`} element={getHerbList(data)} />
      </Routes>
  );
};

const getHerbList = (data) => {
    return (
        <List>
            {data.map((herb, index) => {
                const name = getHerbDisplayName(herb);
                console.log({index, herb, name})
                if (name) {
                    return (
                        <ListItem key={name + index}>
                            <Link to={`/herb/${name}`}>{name}</Link>
                        </ListItem>
                    );
                } else {
                    return <div></div>
                }
            })}
        </List>
    )
}

const getHerbDisplayName = (herb) => {
    return herb["Name"]?.split(",")[0];
}

const parseTSV = (tsvString) => {
  const lines = tsvString.split('\n');
  const header = lines[0].split('\t');
  console.log({header})
  return lines.slice(1).map(line => {
    const data = line.split('\t');
    console.log({data})
    return header.reduce((obj, nextKey, index) => {
      obj[nextKey] = data[index];
      return obj;
    }, {});
  });
};

export default App;
