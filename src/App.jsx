import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import { Container, List, ListItem } from "@mui/material";

import Search from "./Search.jsx";
import HerbDetail from "./HerbDetail.jsx";
import "./App.css";

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
};

const TSVParser = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const location = useLocation(); // Hook to get the current location

  useEffect(() => {
    fetch("/merged_herbs.json")
      .then((response) => response.json())
      .then((herbsData) => {
        setData(herbsData);
        setFilteredData(herbsData);
      })
      .catch((error) => console.error("Error fetching herbs data:", error));
  }, []);

  const isHerbDetailPage = location.pathname.startsWith("/herb/");

  // console.log("data", data)
  return (
    <div>
      {
        <Search
          data={data}
          setFilteredData={setFilteredData}
          visible={!isHerbDetailPage}
        />
      }
      <Routes>
        {filteredData.map((herb) => {
          const name = getHerbDisplayName(herb);
          return (
            <Route
              key={name}
              path={`/herb/${name}`}
              element={<HerbDetail herb={herb} />}
            />
          );
        })}
        <Route key={"home"} path={`/`} element={getHerbList(filteredData)} />
      </Routes>
    </div>
  );
};

const getHerbList = (data) => {
  return (
    <List>
      {data.map((herb, index) => {
        const name = getHerbDisplayName(herb);
        // console.log({index, herb, name})
        if (name) {
          return (
            <ListItem key={name + index}>
              <Link to={`/herb/${name}`}>{name}</Link>
            </ListItem>
          );
        } else {
          return <div></div>;
        }
      })}
    </List>
  );
};

const getHerbDisplayName = (herb) => {
  // Extract name from the JSON structure
  const names = herb?.Names?.Name;
  if (Array.isArray(names) && names.length > 0) {
    return names[0];
  }
  return names || "Unknown Herb";
};

export default App;
