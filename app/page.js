"use client";

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Location from './components/Location';

export default function Home() {
  const [locationData, setLocationData] = useState(null);
  const [userText, setUserText] = useState("");
  const [category, setCategory] = useState("");
  const router = useRouter();

  const handleInputChange = (e) => {
    setUserText(e.target.value);
  }

  const getRecommendations = () => {
    if (userText && locationData) {
      router.push(`/results?request=${encodeURIComponent(userText)}&category=${encodeURIComponent(category)}&location=${encodeURIComponent(locationData)}`);
    } else {
      alert("Please enter a request and fetch your location.");
    }
  }

  return (
    <div className="pt-10">
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 flex items-center justify-center">
        <main className="container">
          <section className="py-4">
            <div className="container overflow-hidden">
              <div className="mb-10 flex flex-col items-center gap-6 text-center">
                <div className="inline-flex font-semibold">AI Powered</div>
              </div>
              <div className="text-center">
                <h1 className="text-4xl font-semibold lg:text-6xl">
                  Your Ultimate <br/> Purchase Companion
                </h1>
              </div>
            </div>
          </section>

          <section className="py-4 text-center">
            <div className="flex flex-col items-center gap-6">

              {}
              <div className="flex items-center gap-4">
                <label className="font-semibold">What do you want the best of?</label>
                  <input
                    type="text"
                    value={userText}
                    onChange={handleInputChange}
                    className="pt-2 pb-1 w-64 text-white text-center font-semibold border-b-1 focus:outline-none"
                  />
              </div>
            </div>

            <div className="pt-2">
              { !locationData ? <Location setLocationData={setLocationData}/> : <p className="py-4">Location: {locationData}</p> }
              
            </div>

            <div className="text-center flex gap-4 justify-center py-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="category"
                  value="food"
                  checked={category === "food"}
                  onChange={(e) => setCategory(e.target.value)}
                />
                Food Item
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="category"
                  value="service"
                  checked={category === "service"}
                  onChange={(e) => setCategory(e.target.value)}
                />
                Service
              </label>
          </div>

            <button type="button" className="mt-10 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
            onClick={getRecommendations}>Get Recommendations</button>

          </section>
        </main>
      </main>
    </div>
  );
}
