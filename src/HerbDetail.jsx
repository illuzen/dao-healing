import React from "react";
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  ImageList,
  ImageListItem,
  Link,
  Button,
  IconButton,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useNavigate } from "react-router-dom";

const HerbProperty = ({ title, content }) => (
  <Box mb={4}>
    <Typography variant="h5" gutterBottom>
      {title}
    </Typography>
    <hr />
    {typeof content === 'object' && content !== null ? (
      content
    ) : (
      <Typography variant="body1">{content}</Typography>
    )}
  </Box>
);

const HerbDetail = ({ herb }) => {
  const navigate = useNavigate();

  if (!herb) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Herb not found
        </Typography>
      </Container>
    );
  }

  const languageNames = {
    Name: herb?.Names?.Name?.join(", ") || "N/A",
    Pharmaceutical: herb?.Names?.Pharmaceutical?.join(", ") || "N/A",
    Biological: herb?.Names?.Biological?.join(", ") || "N/A",
    Common: herb?.Names?.Common?.join(", ") || "N/A",
    Other: (herb?.Names?.["Other name"] || herb?.Names?.["Other"])?.join(", ") || "N/A",
    Chinese: herb?.Names?.Chinese?.join(", ") || "N/A",
    Korean: herb?.Names?.["Pronunciation in Korean"]?.join(", ") || "N/A",
    Japanese: herb?.Names?.["Pronunciation in Japanese"]?.join(", ") || "N/A",
    Cantonese: herb?.Names?.["Pronunciation in Cantonese"]?.join(", ") || "N/A",
  };

  const detailProperties = [
    {
      title: "Geography",
      content: formatGeography(herb?.Geography),
      isComponent: true,
    },
    {
      title: "Properties",
      content: formatProperties(herb?.Properties),
      isComponent: true,
    },
    {
      title: "Meridians",
      content: formatMeridians(herb?.Meridians),
      isComponent: true,
    },
    {
      title: "Maladies Treated",
      content: formatMaladiesTreated(herb?.["Maladies Treated"]),
      isComponent: true,
    },
    {
      title: "Medical Function",
      content: formatMedicalFunction(herb?.["Medical Function"]),
      isComponent: true,
    },
    {
      title: "Chemical Ingredients",
      content: formatChemicalIngredients(herb?.["Chemical Ingredients"]),
      isComponent: true,
    },
    { title: "Dosage", content: herb?.Dosage || "N/A" },
    {
      title: "Samples of Formulae",
      content: herb?.["Samples of Formulae"] || "N/A",
    },
    { title: "Contraindications", content: herb?.Contraindications || "N/A" },
    { title: "Research", content: herb?.Research || "N/A" },
    { title: "Notes", content: herb?.Notes || "N/A" },
  ];

  function formatChemicalIngredients(ingredients) {
    if (!ingredients) return "N/A";
    if (typeof ingredients === "string") return ingredients;
    if (Array.isArray(ingredients)) {
      return (
        <div>
          {ingredients.map((ingredient, index) => (
            <div key={index} style={{ marginBottom: "8px" }}>
              • {ingredient}
            </div>
          ))}
        </div>
      );
    }
    if (typeof ingredients === "object") {
      return (
        <div>
          {Object.entries(ingredients).map(([category, items], index) => (
            <div key={index} style={{ marginBottom: "16px" }}>
              <Typography variant="h6" style={{ fontWeight: "bold", marginBottom: "8px" }}>
                {category}:
              </Typography>
              <div style={{ paddingLeft: "16px" }}>
                {Array.isArray(items) ? (
                  items.map((item, itemIndex) => (
                    <div key={itemIndex} style={{ marginBottom: "4px" }}>
                      • {item}
                    </div>
                  ))
                ) : typeof items === "object" && items !== null ? (
                  // Handle nested objects like "Compounds" -> {"Sterols": [...], "Sugars": [...]}
                  <div>
                    {Object.entries(items).map(([subCategory, subItems], subIndex) => (
                      <div key={subIndex} style={{ marginBottom: "12px" }}>
                        <Typography variant="subtitle1" style={{ fontWeight: "bold", marginBottom: "4px" }}>
                          {subCategory.replace(/_/g, ' ')}:
                        </Typography>
                        <div style={{ paddingLeft: "16px" }}>
                          {Array.isArray(subItems) ? (
                            subItems.map((subItem, subItemIndex) => (
                              <div key={subItemIndex} style={{ marginBottom: "4px" }}>
                                • {subItem}
                              </div>
                            ))
                          ) : (
                            <div>• {subItems}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div>• {items}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      );
    }
    return "N/A";
  }

  function formatMedicalFunction(medicalFunction) {
    if (!medicalFunction) return "N/A";
    if (typeof medicalFunction === "string") {
      // Split by common delimiters and create a list
      const functions = medicalFunction
        .split(/[,;]\s*/)
        .filter(item => item.trim().length > 0);
      
      if (functions.length <= 1) {
        return <div>• {medicalFunction}</div>;
      }
      
      return (
        <div>
          {functions.map((func, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {func.trim()}
            </div>
          ))}
        </div>
      );
    }
    if (Array.isArray(medicalFunction)) {
      return (
        <div>
          {medicalFunction.map((func, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {func}
            </div>
          ))}
        </div>
      );
    }
    return "N/A";
  }

  function formatMaladiesTreated(maladies) {
    if (!maladies) return "N/A";
    if (typeof maladies === "string") {
      // Split by common delimiters and create a list
      const maladiesList = maladies
        .split(/[,;]\s*/)
        .filter(item => item.trim().length > 0);
      
      if (maladiesList.length <= 1) {
        return <div>• {maladies}</div>;
      }
      
      return (
        <div>
          {maladiesList.map((malady, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {malady.trim()}
            </div>
          ))}
        </div>
      );
    }
    if (Array.isArray(maladies)) {
      return (
        <div>
          {maladies.map((malady, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {malady}
            </div>
          ))}
        </div>
      );
    }
    return "N/A";
  }

  function formatGeography(geography) {
    if (!geography) return "N/A";
    if (typeof geography === "string") {
      // Split by common delimiters and create a list
      const locations = geography
        .split(/[,;]\s*/)
        .filter(item => item.trim().length > 0);
      
      if (locations.length <= 1) {
        return <div>• {geography}</div>;
      }
      
      return (
        <div>
          {locations.map((location, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {location.trim()}
            </div>
          ))}
        </div>
      );
    }
    if (Array.isArray(geography)) {
      return (
        <div>
          {geography.map((location, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {location}
            </div>
          ))}
        </div>
      );
    }
    return "N/A";
  }

  function formatProperties(properties) {
    if (!properties) return "N/A";
    if (typeof properties === "string") {
      // Split by common delimiters and create a list
      const propsList = properties
        .split(/[,;]\s*/)
        .filter(item => item.trim().length > 0);
      
      if (propsList.length <= 1) {
        return <div>• {properties}</div>;
      }
      
      return (
        <div>
          {propsList.map((prop, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {prop.trim()}
            </div>
          ))}
        </div>
      );
    }
    if (Array.isArray(properties)) {
      return (
        <div>
          {properties.map((prop, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {prop}
            </div>
          ))}
        </div>
      );
    }
    return "N/A";
  }

  function formatMeridians(meridians) {
    if (!meridians) return "N/A";
    if (typeof meridians === "string") {
      // Split by common delimiters and create a list
      const meridiansList = meridians
        .split(/[,;]\s*/)
        .filter(item => item.trim().length > 0);
      
      if (meridiansList.length <= 1) {
        return <div>• {meridians}</div>;
      }
      
      return (
        <div>
          {meridiansList.map((meridian, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {meridian.trim()}
            </div>
          ))}
        </div>
      );
    }
    if (Array.isArray(meridians)) {
      return (
        <div>
          {meridians.map((meridian, index) => (
            <div key={index} style={{ marginBottom: "4px" }}>
              • {meridian}
            </div>
          ))}
        </div>
      );
    }
    return "N/A";
  }

  function renderScientificPapers(papers) {
    return papers.split(",").map((url, index) => (
      <Box key={index} sx={{ my: 1 }}>
        <Link href={url} target="_blank" rel="noopener noreferrer">
          {url}
        </Link>
      </Box>
    ));
  }

  return (
    <Paper elevation={0}>
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          variant="outlined"
          sx={{ mb: 2 }}
        >
          Back to Herbs
        </Button>
      </Box>
      {/*<ImageList cols={3} gap={8}>*/}
      {/*    {herb["Image Links"].split(',').map((url, index) => (*/}
      {/*    <ImageListItem key={index}>*/}
      {/*        <img src={url} alt={`Herb ${index + 1}`} loading="lazy" />*/}
      {/*    </ImageListItem>*/}
      {/*    ))}*/}
      {/*</ImageList>*/}
      <Box mb={2}>
        <Typography variant="h4" component="h1" style={{ fontWeight: 'bold', textTransform: 'capitalize', marginBottom: '4px' }}>
          {herb?.Names?.Name?.[0] || "Unknown"}
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          {herb?.Type?.toLowerCase() || "herb"}
        </Typography>
      </Box>
      <TableContainer component={Paper}>
        <Table size="small" aria-label="herb table">
          <TableHead>
            <TableRow>
              <TableCell>Language</TableCell>
              <TableCell align="left">Name</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(languageNames)
              .filter(([language, name]) => name && name !== "N/A" && name.trim() !== "")
              .map(([language, name]) => (
                <TableRow key={language}>
                  <TableCell component="th" scope="row">
                    {language}
                  </TableCell>
                  <TableCell align="left">{name}</TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box mt={4}>
        {detailProperties.map((detail, index) => {
          // Check raw data before formatting for isComponent fields
          if (detail.isComponent) {
            let rawData;
            switch (detail.title) {
              case "Geography":
                rawData = herb?.Geography;
                break;
              case "Properties":
                rawData = herb?.Properties;
                break;
              case "Meridians":
                rawData = herb?.Meridians;
                break;
              case "Maladies Treated":
                rawData = herb?.["Maladies Treated"];
                break;
              case "Medical Function":
                rawData = herb?.["Medical Function"];
                break;
              case "Chemical Ingredients":
                rawData = herb?.["Chemical Ingredients"];
                break;
              default:
                rawData = detail.content;
            }
            
            // Check if raw data is empty
            if (!rawData || 
                (Array.isArray(rawData) && rawData.length === 0) ||
                (typeof rawData === 'object' && Object.keys(rawData).length === 0) ||
                (typeof rawData === 'string' && rawData.trim() === '')) {
              return null;
            }
          } else {
            // For non-component fields, check the content directly
            if (!detail.content || detail.content === "N/A" || 
                (typeof detail.content === 'string' && detail.content.trim().length <= 2)) {
              return null;
            }
          }
          
          return (
            <HerbProperty
              key={index}
              title={detail.title}
              content={detail.content}
            />
          );
        })}
      </Box>
    </Paper>
  );
};

export default HerbDetail;
