import { Locator, Header, Footer } from './components'

import 'bootstrap/dist/css/bootstrap.css'
import '../css/App.css'

const App = ( {title} ) => {
    return (
        <>
            <Header/>
            <Locator/>
            <Footer />
        </>
    );
}
export default App;
