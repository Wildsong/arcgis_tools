import { Card } from 'react-bootstrap'
import { AppSettings } from '../appSettings';
import { version } from '../../package.json'
import 'bootstrap/dist/css/bootstrap.css'
import '../../css/App.css'


const DISCLAIMER="Every effort has been made \
to offer the most current and correct information possible on these pages. \
The information included on these pages has been compiled by \
County staff from a variety of sources, and is subject to change without notice. \
Clatsop County makes no warranties or representations \
whatsoever regarding the quality, content, completeness, accuracy or \
adequacy of such information and data. Clatsop County reserves \
the right to make changes at any time without notice. Original records \
may differ from the information on these pages. Interest and discounts, \
if available, may not be accurately reflected here. Verification \
of information on source documents is recommended. By using this application, \
you assume all risks arising out of or associated with access to these pages, \
including but not limited to risks of damage to your computer, peripherals, \
software and data from any virus, software, file or other cause associated \
with access to this application. \
Clatsop County shall not be liable for any damages whatsoever arising out \
of any cause relating to use of this application, \
including but not limited to mistakes, omissions, deletions, errors, \
or defects in any information contained in these pages, \
or any failure to receive or delay in receiving information.";

export const Footer = () => {
    const client_version = 'version ' + version
    let server_url = "";
    if (process.env.NODE_ENV !== 'production') {
        server_url = AppSettings.SERVER;
    }
    return (
        <footer>
            ©2023 Clatsop County, Oregon <br/>
            {client_version} Server status: <Ping /> &nbsp;
            <a target="api" href={server_url}>{server_url}</a>
            <div className="disclaimer">
                {DISCLAIMER}
            </div>
        </footer>
    );
}

