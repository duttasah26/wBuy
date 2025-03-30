'use client';

import { useEffect, useState } from "react";

export default function Location( {setLocationData}) {
    const [location, setLocation] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchLocation = () => {
        setLoading(true);
        fetch("https://ipapi.co/json/")
            .then((res) => res.json())
            .then((data) => {
            const locationInfo = `${data.city}, ${data.region}`;
            setLocation(locationInfo);
            if (setLocationData) setLocationData(locationInfo); // Pass to parent if needed
            })
            .catch((err) => {console.error("Error fetching location:", err) })
            .finally(() => setLoading(false));
        };
  
    return (
        <div>
          <button onClick={fetchLocation} disabled={loading} className="text-white mt-5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Get My Location</button>

          {loading ? "Fetching location..." : ""}
    
          {location && <p>Your Location: {location}</p>}
      </div>
    );
};
  
