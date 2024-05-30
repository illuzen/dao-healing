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
    <Box mb={4}>
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
    "Name": herb["Name"],
    "Cantonese": herb["Cantonese - 粵語發音"],
    "Pharmaceutical": herb["Pharmaceutical Name - 英文药名"],
    "Latin": herb["Latin Name - 拉丁名"],
    "Japanese": herb["Japanese Name - 日語"],
    "Korean": herb["Korean Name - 韓語"],
    "Other Name": herb["Other Name - 別名"],
    "Common Name": herb["Common Name - 英文名"]
  };

  const detailProperties = [
    { title: "Distribution", content: herb["Distribution - 分佈"] },
    { title: "Properties & Characteristics", content: herb["Properties / Characteristics - 性味"] },
    { title: "Meridians Entered", content: herb["Meridians Entered - 歸經"] },
    { title: "Actions & Indications", content: herb["Actions & Indications - 主治"] },
    { title: "Medical Function", content: herb["Medical Function - 藥理"] },
    { title: "Chemical Ingredients", content: herb["Chemical Ingredients - 化學成份"] },
    { title: "Daily Dosage", content: herb["Daily Dosage - 每日用量"] },
    { title: "Contraindications & Toxicity", content: herb["Contraindications / Toxicity - 毒素與禁忌"] },
    { title: "Modern Application", content: herb["Modern Application - 現代應用"] },
    { title: "Samples of Formulae", content: herb["Samples of Formulae - 處方舉例"] },
    { title: "Note", content: herb["Note - 註"] },
  ];

  function renderScientificPapers(papers) {
    return papers.split(',').map((url, index) => (
      <Box key={index} sx={{ my: 1 }}>
        <Link href={url} target="_blank" rel="noopener noreferrer">
          {url}
        </Link>
      </Box>
    ));
  }
  
  return (
    <Paper elevation={0}>
        {/*<ImageList cols={3} gap={8}>*/}
        {/*    {herb["Image Links"].split(',').map((url, index) => (*/}
        {/*    <ImageListItem key={index}>*/}
        {/*        <img src={url} alt={`Herb ${index + 1}`} loading="lazy" />*/}
        {/*    </ImageListItem>*/}
        {/*    ))}*/}
        {/*</ImageList>*/}
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
                detail.content.length > 2 ?
                <HerbProperty key={index} title={detail.title} content={detail.content} />
                    : null
            ))}
        </Box>
    </Paper>
  );
};

export default HerbDetail;
