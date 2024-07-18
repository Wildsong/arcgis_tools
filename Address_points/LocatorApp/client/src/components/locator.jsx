import React from 'react'
import { useEffect, useState } from 'react';   // eslint-disable-line no-unused-vars
import { Form, InputGroup, Button, Container, Spinner } from 'react-bootstrap'
import 'tippy.js/dist/tippy.css' // optional

const InstrumentList = (props) => {
    const [row, setRow] = useState(0);
    const { loading, error, data } = useQuery(GET_INSTRUMENTS, {variables: {...props.params}});
    if (error) {
        let gqlmsg = '';
        let emailmsg = 'mailto:gisinfo@clatsopcounty.gov?subject=Records%20app%20error';
        try {
            if (error.named === 'ApolloError') {
                gqlmsg = 'GQL server is offline.';
            } else {
                // There might be an additional code, or not.
                gqlmsg = error.graphQLErrors[0].extensions.code;
            }
        } catch (e) {
            gqlmsg = `Database server is offline. (${e.message})`;
        }
        emailmsg += '&body=' + encodeURI(error.message + '\n' + gqlmsg);
        return (
            <Container>
            <h4>Error: {error.message}</h4>
            <b>{gqlmsg}</b>
            <p>
                Please reload the page and try again. If the problem persists let us know about it.
                <br /><a href={emailmsg}>Send email</a>
            </p>
            </Container>
        );
    }
    if (loading) {
        return (
            <Container>
                <Spinner animation='border' role='status'>
                    <span className="visually-hidden">Searching...</span>
                </Spinner>
            </Container>
        );
    }

    if (!data || !data.instruments) {
        // This fires when the form is empty.
        return (
            <Container><i>Enter a search term in the form.</i></Container>
        )
    }

    const instruments = data.instruments;
    if (instruments.length == 0) {
        return (
            <Container><i>No matches found.</i></Container>
        )
    }

    return (
        <Container>
            <InstrumentDetail row={row}/>
            <DataTable list={instruments} selectedrow={setRow}/>
        </Container>
    );
}

const Search = (props) => {
    return 
        <>
        search form
        </>
}

/**
 * This is the main component of the app,
 * including the search form and results list.
 * @returns results of query operations
 */
const Locator = () => {
    const [input,setInput] = useState({
        "address": '',
    });
    return (
        <>
            <h3>Address Search</h3>
            <Search setinput={setInput}/>
            <AddressList params={input}/>
        </>
    )
}
export default Instruments;

