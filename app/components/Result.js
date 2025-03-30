const Result = ({ name, key_features, rating, quotes }) => {
    return (
        <>
            <div className="w-full max-w-4xl mx-auto my-6 text-white rounded-lg shadow-lg overflow-hidden flex border">
                <div className="w-1/3 p-4 flex flex-col items-center justify-center">
                    <h3 className="text-lg font-semibold mb-2">{name}</h3>
                    <img src="https://avatar.iran.liara.run/public" alt="Card image" class="w-40 h-40 object-cover"/>
                </div>

                <div className="w-2/3 p-4">
                    <div className="text-sm text-gray-500 mt-2">
                        <div className="flex items-start mb-4">
                            <h4 className="mr-2 font-semibold">Users said they have:</h4>
                            <ul className="list-none pl-4 text-start">
                                {key_features.map((feature, i) => (
                                    <li key={i} className="text-white">{feature}</li>
                                ))}
                            </ul>
                        </div>
                        
                        <div className="flex items-start mb-4">
                            <h4 className="mr-2 font-semibold">Rating:</h4>
                            <p className="text-white">{rating || "No rating available"}</p>
                        </div>

                        <div className="flex items-start mb-4">
                            <h4 className="mr-2 font-semibold">Quotes:</h4>
                            <ul className="list-none pl-4 text-start">
                                {quotes.map((review, j) => (
                                    <li key={j} className="text-white italic">{review}</li>
                                ))}
                            </ul>
                        </div> 
                    </div>
                </div>
            </div>
        </>
    )
}

export default Result;