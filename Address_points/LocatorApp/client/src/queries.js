/*

FIXME: I would like to code these directly as .graphql files
but I don't know how to do that yet.

See https://parceljs.org/languages/graphql/

*/
import { gql, useQuery } from '@apollo/client'

export const GET_INSTRUMENTS = gql`
    query GetInstruments(
        $querytype:QueryType!,
        $lastname:String,
        $firstname:String,
        $description:String,
        $startdate:String,
        $enddate:String
    ) {
        instruments(
            querytype:$querytype, 
            lastname:$lastname, 
            firstname:$firstname,
            description:$description,
            startdate:$startdate,
            enddate:$enddate
        ) {
            id
            instrument_id
            instrument_type_id
            instrument_description
            recording_description
            recording_date
            firstname
            middlename
            lastname
            description
            bp_type
            number_of_pages
            book
            page
            party_type
            original_instrument
            original_book
            original_page
            consideration_amount
        }
    }
`;

export const PING = gql`
    query Ping {
        ping {
            timestamp
            version
        }
    }
`;
