import React from 'react';

const HerbDetail = ({ herb }) => {
    if (!herb) {
        return <div>Herb not found</div>;
    }

    return (
        <div className="herb-detail">
            <h2>
                {herb["English Name"]} -
                {herb["Mandarin Name"]} -
                {herb["Cantonese Name"]} -
                {herb["Latin Name"]} -
                {herb["Japanese Name"]} -
                {herb["Korean Name"]} -
                {herb["German Name"]} -
                {herb["French Name"]} -
                {herb["Spanish Name"]}
            </h2>
            {
                herb["Image Links"].split(',').map((url, index) => (
                    <img key={index} src={url} alt={`Image ${index + 1}`} style={{ margin: '10px', width: '200px' }} />
                ))
            }
            <div className="herb-info">
                <p><strong>🌿 Description:</strong> {herb["Description"]}</p>
                <p><strong>🗃️ Category:</strong> {herb["Herb Category"]}</p>
                <p><strong>🌡️ Temperature:</strong> {herb["Temperature"]}</p>
                <p><strong>😝 Taste:</strong> {herb["Taste"]}</p>
                <p><strong>🧬 Meridian Affinity:</strong>
                    {herb["Meridian Affinity"].split(",").join(", ")}
                </p>
                <p><strong>🤢 Related Ailments:</strong> {herb["Related Ailments"]}</p>
                <p><strong>💉 Dosage Range:</strong> {herb["Dosage Range"]}</p>
                <p><strong>⛔ Contraindications:</strong> {herb["Contraindications"]}</p>
                <p><strong>🧪 Interactions:</strong> {herb["Interactions"]}</p>
                <p><strong>⚗️ Preparation Method:</strong> {herb["Preparation Method"]}</p>
                <p><strong>🌏 Geographic Source:</strong> {herb["GeographicSource"]}</p>
                <p><strong>🔍 Availability:</strong> {herb["Availability"]}</p>
                <p><strong>💰 Price Range:</strong> {herb["PriceRange"]}</p>
                <div><strong>🔬 Scientific Papers:</strong>
                    {herb["Scientific Papers"].split(",").map((url, index) =>
                        (<div key={index} >
                            <a href={url} target="_blank" rel="noopener noreferrer">{url.substring(0, 40)}...</a>
                        </div>))
                    }
                </div>
            </div>
        </div>
    );
}

export default HerbDetail;
