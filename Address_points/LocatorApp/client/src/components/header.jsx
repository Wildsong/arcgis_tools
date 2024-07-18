import { Nav, Navbar, Container } from 'react-bootstrap'

export const Header = () => {
    let logoUrl = (new URL('../../assets/logo_100.png', import.meta.url)).toString();

    return (
        <header className="page_header">
            <div className="branding">
                <div className="page-header__branding branding">
                    <div className="region region-branding">
                        <div id="block-municodebrandingblock" className="block block-municode-base block-municode-branding-block">
                            <div className="block__content">
                                <div className="branding">
                                    <a href="/" id="logo" className="branding__link">
                                        <span className="branding__image-wrapper">
                                        <img src={logoUrl} alt="Clatsop County Oregon 1844" className="branding__image"/>
                                        </span>
                                        <span className="branding__text">
                                            <span className="branding__text--item branding__text--city">Clatsop County</span>
                                            <span className="branding__text--item branding__text--state">Oregon</span>
                                        </span>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
