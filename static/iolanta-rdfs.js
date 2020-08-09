import {Slim} from './lib/Slim.js';
import './lib/directives/repeat.js';

Slim.tag(
  'iolanta-rdfs-entity-cards',
  `
      <div class="ui four cards">
        <div class="ui card" s:repeat="items as item" bind>
          <div class="content">
            <div class="header">{{item.label}}</div>
            <div class="meta">
              <span class="category">
                subclass of <strong>{{item.superclass.label}}</strong>
              </span>
            </div>
            <div class="description">{{item.comment}}</div>
          </div>
          <div class="extra content">
            <small class="right floated">{{item.prefixed_id}}</small>
          </div>
        </div>
      </div>
    `,
  class IolantaRDFSEntityCard extends Slim {
    retrieve_query_text() {
      return fetch('/iolanta-rdfs.sparql').then(
        response => response.text()
      )
    }

    perform_query(query_text) {
      console.log(query_text);
      return fetch('/sparql', {
        method: 'post',
        body: JSON.stringify({
          'query': query_text,
          'context': {
            '@vocab': 'http://www.w3.org/2000/01/rdf-schema#',
            'meta': 'https://iolanta.tech/apps/iolanta-rdfs/meta'
          }
        }),
      }).then(
        response => response.json(),
      ).then(
        console.log,
      )
    }

    onBeforeCreated() {
      this.retrieve_query_text().then(
        this.perform_query,
      );

      this.items = [{
        label: 'foo',
        superclass: {
          label: 'boo',
        },
        comment: 'bar',
        prefixed_id: 'baz',
      }]
    }
  }
)
