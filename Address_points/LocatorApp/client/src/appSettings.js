
export const AppSettings = {
    SERVER : (process.env.NODE_ENV == 'production')
        ? 'https://foxtrot.clatsopcounty.gov/api' 
        : 'http://localhost:4000/api'
}

