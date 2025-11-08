import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import { Container, Grid, Card, CardContent, Typography, Chip, Box, AppBar, Toolbar } from "@mui/material";

import Search from "./Search.jsx";
import HerbDetail from "./HerbDetail.jsx";
import "./App.css";

const App = () => {
  return (
    <Router>
      <Container>
        <div className="App">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <img 
              src="/dragon.avif" 
              alt="Dragon Logo" 
              style={{ 
                height: '80px', 
                width: 'auto', 
                marginBottom: '16px' 
              }} 
            />
            <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: 'black' }}>
              Chinese Herb Library
            </Typography>
          </Box>

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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {data.map((herb, index) => {
          const name = getHerbDisplayName(herb);
          if (name) {
            return (
              <Grid item xs={12} sm={6} md={4} key={name + index}>
                <Card 
                  component={Link} 
                  to={`/herb/${name}`}
                  sx={{ 
                    height: 320,
                    display: 'flex',
                    flexDirection: 'column',
                    textDecoration: 'none',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 3
                    }
                  }}
                >
                  <CardContent sx={{ flexGrow: 1, p: 2, overflow: 'hidden' }}>
                    <Box sx={{ mx: 1, my: 2, mb: 4 }}>
                      <Typography 
                        variant="h5" 
                        component="h2" 
                        gutterBottom 
                        sx={{ 
                          fontWeight: 'bold',
                          textTransform: 'capitalize',
                          color: 'black',
                          mb: 2,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {name}
                      </Typography>
                      
                      {herb?.Properties && herb.Properties.length > 0 && (
                        <Box sx={{ mb: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {herb.Properties.slice(0, 3).map((property, idx) => (
                            <Chip 
                              key={idx}
                              label={property} 
                              size="small" 
                              sx={{ backgroundColor: '#850206', color: 'white' }}
                            />
                          ))}
                        </Box>
                      )}
                      
                      {herb?.Meridians && herb.Meridians.length > 0 && (
                        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {herb.Meridians.slice(0, 2).map((meridian, idx) => (
                            <Chip 
                              key={idx}
                              label={meridian} 
                              size="small" 
                              sx={{ backgroundColor: '#fbaf2b', color: 'white' }}
                            />
                          ))}
                        </Box>
                      )}
                      
                      {herb?.Names?.Chinese && herb.Names.Chinese.length > 0 && (
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            mb: 1
                          }}
                        >
                          {herb.Names.Chinese[0]}
                        </Typography>
                      )}
                      
                      {herb?.Names?.Biological && herb.Names.Biological.length > 0 && (
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            fontStyle: 'italic',
                            mb: 2
                          }}
                        >
                          {herb.Names.Biological[0]}
                        </Typography>
                      )}
                      
                      {herb?.["Maladies Treated"] && herb["Maladies Treated"].length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Used for:
                          </Typography>
                          <Typography 
                            variant="body2" 
                            color="text.secondary"
                            sx={{
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              lineHeight: 1.4
                            }}
                          >
                            {herb["Maladies Treated"].slice(0, 3).join(', ')}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          } else {
            return null;
          }
        })}
      </Grid>
    </Container>
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
