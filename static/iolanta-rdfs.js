import {Slim} from './lib/Slim.js';
import './lib/directives/repeat.js';
import './lib/directives/if.js';

Slim.tag(
  'iolanta-rdfs-blocks',
  `
    <div s:if="blocks" bind>
      <div bind:class="cls" bind>
          <div class="ui card" s:repeat="blocks as block" bind>
            <div class="content">
              <div class="header">{{block.label}}</div>
              <div class="meta">
                {{block.@type}}
              </div>
              <div class="description">{{block.comment}}</div>
            </div>
            <div class="extra content">
              <small class="right floated">{{block.@id}}</small>
            </div>
          </div>
        </div>
    </div>
  `,
  class extends Slim {
    onAdded() {
      if(this.blocks) {
        let word = {
          1: 'two',
          2: 'two',
          3: 'four',
          4: 'four'
        }[this.blocks.length];

        this.cls = `ui stackable ${word} cards`;
      } else {
        this.cls = 'ui stackable cards';
      }
    }
  },
);


Slim.tag(
  'iolanta-rdfs-subsections',
  `
    <div class="ui two column stackable grid" s:if="sections" bind>
      <div class="column" s:repeat="sections as section" bind>
        <h3 class="ui header">{{section.label}}</h3>
        <iolanta-rdfs-blocks bind:blocks="section.blocks"></iolanta-rdfs-blocks>
      </div>
    </div>
  `,
  class extends Slim {
    onAdded() {
      if(this.sections) {
        this.sections.sort(
          (section1, section2) => section1.index - section2.index,
        )
      }
    }
  },
)


Slim.tag(
  'iolanta-rdfs-entity-cards',
  `
    <style>
      h2.header { margin-top: 1em !important; }
    </style>
    <h1 class="ui header">
      {{ontology.label}}
      <div class="sub header">is an <strong>{{ontology.meta.label}}</strong></div>
    </h1>

    <div class="ui container" s:repeat="ontology.sections as section" bind>
      <h2 class="ui header">{{section.label}}</h2>

      <iolanta-rdfs-blocks bind:blocks="section.blocks"></iolanta-rdfs-blocks>
      <iolanta-rdfs-subsections bind:sections="section.sections"></iolanta-rdfs-subsections>
    </div>
    `,
  class IolantaRDFSEntityCard extends Slim {
    retrieve_query_text() {
      return fetch('/iolanta-rdfs.sparql').then(
        response => response.text()
      )
    }

    describe() {
      return fetch('/view/?iri=http://www.w3.org/2000/01/rdf-schema%23').then(
        response => response.json()
      )
    }

    onBeforeCreated() {
      function process_section(section) {
        // This function is sorting sections, subsections, and blocks to make sure they don't change
        // their location between page refreshes.
        // This does not look very well and is very ad-hoc. I can't sort these in the appropriate
        // components because either
        //   1) my lifecycle handler runs too early, meaning the variables are
        //      not even available yet, or
        //   2) it runs too late, and the limitations of s:repeat mean that, however I sort the data,
        //      it will make no changes to what the user sees.
        if (section.blocks) {
          section.blocks.sort(
            (block1, block2) => block1.label < block2.label ? -1 : 1,
          );
        }

        if (section.sections) {
          section.sections.sort(
            (section1, section2) => section1.index - section2.index,
          )

          section.sections = section.sections.map(process_section);
        }

        return section;
      }

      let self = this;
      this.describe().then(
        data => {
          data.sections = data.sections.map(process_section);
          data.sections.sort(
            (section1, section2) => section1.index - section2.index,
          )

          self.ontology = data;
        }
      );
    }
  }
)
