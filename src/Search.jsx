import React, { useState } from 'react';
import TextField from '@mui/material/TextField';

const Search = ({ data, setFilteredData, visible }) => {
    console.log({data})
    const [searchTerm, setSearchTerm] = useState('');

    if (!visible) {
        return null;
    }

    const handleSearch = (event) => {
        const value = event.target.value.toLowerCase();
        setSearchTerm(value);
        const filtered = data.filter(entry =>
            Object.values(entry).some(val =>
                String(val).toLowerCase().includes(value)
            )
        );
        setFilteredData(filtered);
    };



    return (
        <TextField
            label="Search"
            variant="outlined"
            fullWidth
            value={searchTerm}
            onChange={handleSearch}
        />
    );
};

export default Search;
