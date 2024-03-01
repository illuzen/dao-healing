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
//    "Mandarin": herb["Mandarin Name"],
    "Cantonese": herb["Cantonese - 粵語發音"],
    "Pharmaceutical": herb["Pharmaceutical Name - 英文药名"],
    "Latin": herb["Latin Name - 拉丁名"],
    "Japanese": herb["Japanese Name - 日語"],
    "Korean": herb["Korean Name - 韓語"],
//    "German": herb["German Name"],
//    "French": herb["French Name"],
//    "Spanish": herb["Spanish Name"]
    "Other Name": herb["Other Name - 別名"]
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
//    { title: "Commonly Used Formulae", content: herb["Commonly Used Formulae - 常用配方"] }, - 10 has an entry, move to "Samples of Formulae" column
    { title: "Contraindications & Toxicity", content: herb["Contraindications / Toxicity - 毒素與禁忌"] },
    { title: "Modern Application", content: herb["Modern Application - 現代應用"] },
//    in "Modern Application" some entries are 'to be loaded' or weird character, or references elsewhere. Can it be merged with Actions and Indications?
    { title: "Samples of Formulae", content: herb["Samples of Formulae - 處方舉例"] },
//    combine 'Commonly used formulae and Samples of Formulae columns, a lot of 'to be loaded' entries
//    { title: "Prescription Names", content: herb["Prescription Names - 處方名"] }, - only a couple of entries
//    { title: "Imitated Products Identification Method", content: herb["Imitated Products Identification Method: (to be translated) 偽品鑒別﹕"] }, - has only one entry row 17, add it to the Note column
    { title: "Note", content: herb["Note - 註"] },
//    { title: "Adulteration", content: herb["Adulteration:"] }, - has one entry Ginseng row 64, add to Note column, same to Price and Quality column
//"Clinical Application" column only 2 entries - AB 168, AB 324 - add to 'Actions and Indications'
//flavonoids AC 77
//row 77 only one plant in columns AC-AS in Chinese
//row 95 is the only one plant in column AT, add to Notes
//row 120 is the only one plant for columns: AU-DM
// row 136 only one plant in column - Properties¡G©Ê¨ý¡G, combine with the column 'Properties & Characteristics
//row 142 only one in columnt Uses, combine with Modern Application
//row 168 only one in Folk Name:¥Á¶¡¦WºÙ¡G, combine with Common name
// row 201 the only used in Present Application, combine with 'Actions and Indications'
// row 281, 306, 370 the only ones in DR Antidode, put in Notes
//row 185 the only one in DS, Parts being usded - add to Notes
//row 224 is the only used in DU, Synonyms - add to Other Names
//row 250 is the oly one used in DX Properties性味：- combine with Properties & Characteristics
//row 257 is the only used in DX Sources in Chinese:資料來源：- combine with Notes
// row 260 is the only one used in DY Usage combine with "Modern Application"
//row 294 is the only used in EH Pinyin - 拼音, combine with Notes
//row 373 is the only usd in EI qualify of herb:飲片的質量：, combine with Properties & Characteristics




//    { title: "Description", content: herb["Description"] },
//    { title: "Category", content: herb["Category"] },
//    { title: "Temperature", content: herb["Temperature"] },
//    { title: "Taste", content: herb["Taste"] },
//    { title: "Meridian Affinity", content: herb["Meridian Affinity"].split(",").join(", ") },
//    { title: "Related Ailments", content: herb["Related Ailments"] },
//    { title: "Dosage Range", content: herb["Dosage Range"] },
//    { title: "Contraindications", content: herb["Contraindications"] },
//    { title: "Interactions", content: herb["Interactions"] },
//    { title: "Preparation Method", content: herb["Preparation Method"] },
//    { title: "Geographic Source", content: herb["Geographic Source"] },
//    { title: "Availability", content: herb["Availability"] },
//    { title: "Price Range", content: herb["Price Range"] },
//    { title: "Scientific Papers", content: renderScientificPapers(herb["Scientific Papers"]) },
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
        <ImageList cols={3} gap={8}>
            {herb["Image Links"].split(',').map((url, index) => (
            <ImageListItem key={index}>
                <img src={url} alt={`Herb ${index + 1}`} loading="lazy" />
            </ImageListItem>
            ))}
        </ImageList>
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
    </Paper>
  );
};

export default HerbDetail;
