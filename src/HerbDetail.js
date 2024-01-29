import React from 'react';
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
  Link
} from '@mui/material';

const HerbProperty = ({ title, content }) => (
    <Box mb={4}> {/* Add bottom margin */}
      <Typography variant="h5" gutterBottom>
        {title}
      </Typography>
      <hr />
      <Typography variant="body1">
        {content}
      </Typography>
    </Box>
  );

const HerbDetail = ({ herb }) => {
  if (!herb) {
    return (
      <Container>
        <Typography variant="h5" color="error">Herb not found</Typography>
      </Container>
    );
  }

  const languageNames = {
    "English": herb["English Name"],
    "Mandarin": herb["Mandarin Name"],
    "Cantonese": herb["Cantonese Name"],
    "Latin": herb["Latin Name"],
    "Japanese": herb["Japanese Name"],
    "Korean": herb["Korean Name"],
    "German": herb["German Name"],
    "French": herb["French Name"],
    "Spanish": herb["Spanish Name"]
  };

  const detailProperties = [
    { title: "Description", content: herb["Description"] },
    { title: "Category", content: herb["Category"] },
    { title: "Temperature", content: herb["Temperature"] },
    { title: "Taste", content: herb["Taste"] },
    { title: "Meridian Affinity", content: herb["Meridian Affinity"].split(",").join(", ") },
    { title: "Related Ailments", content: herb["Related Ailments"] },
    { title: "Dosage Range", content: herb["Dosage Range"] },
    { title: "Contraindications", content: herb["Contraindications"] },
    { title: "Interactions", content: herb["Interactions"] },
    { title: "Preparation Method", content: herb["Preparation Method"] },
    { title: "Geographic Source", content: herb["Geographic Source"] },
    { title: "Availability", content: herb["Availability"] },
    { title: "Price Range", content: herb["Price Range"] },
    { title: "Scientific Papers", content: renderScientificPapers(herb["Scientific Papers"]) },
  ];

  function renderScientificPapers(papers) {
    return papers.split(',').map((url, index) => (
        <div>
            <Link key={index} href={url} target="_blank" rel="noopener noreferrer">
                {url}
            </Link>
        </div>
    ));
  }

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 2 }}>
        <ImageList cols={3} gap={8}>
          {herb["Image Links"].split(',').map((url, index) => (
            <ImageListItem key={index}>
              <img src={url} alt={`Herb ${index + 1}`} loading="lazy" />
            </ImageListItem>
          ))}
        </ImageList>
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
                Herb Name by Language
            </Typography>
            <TableContainer component={Paper}>
            <Table size="small" aria-label="herb table">
                <TableHead>
                  <TableRow>
                    <TableCell>Language</TableCell>
                    <TableCell align="left">Name</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(languageNames).map(([language, name]) => (
                    <TableRow key={language}>
                      <TableCell component="th" scope="row">{language}</TableCell>
                      <TableCell align="left">{name}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Box mt={4}>
                {detailProperties.map((detail, index) => (
                <HerbProperty key={index} title={detail.title} content={detail.content} />
                ))}
            </Box>
          </CardContent>
        </Card>
      </Paper>
    </Container>
  );
};

export default HerbDetail;
