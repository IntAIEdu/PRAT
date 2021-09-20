var i, j, node;
// blank space between groups of nodes of the same section
var groupSep = 1;

var nodeRadius = d3.scaleSqrt().range([3, 7]);
var linkWidth = d3.scaleLinear().range([1.5, 2 * nodeRadius.range()[0]]);

var margin = {
    top: nodeRadius.range()[1] + 1,
    right: nodeRadius.range()[1] + 1,
    bottom: nodeRadius.range()[1] + 1,
    left: nodeRadius.range()[1] + 1
};

var rectHeight = 20,
    rectWidth = 40,
    wordFontSize = 10,
    posFontSize = 15,
    edgeFontSize = 10;

var width = 3080 - margin.left - margin.right;
var height = 720 - margin.top - margin.bottom;

var x = d3.scaleLinear().range([0, width]);
//var colors = d3.scale.category20(); // for older versions of d3.js
var colors = d3.scaleOrdinal(d3.schemeCategory20);

var svg = d3.select('svg')
    .attr('width', width + margin.left + margin.right + 100) // FIXME: don't use magic numers to prevent truncation of the svg elements
    .attr('height', height + margin.top + margin.bottom + rectHeight + 10)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

d3.json('../datasets/parsed_first_sentence.json', function (error, graph) {
    if (error) throw error;

    var idToNode = {};
    /* DELETED
    var sectionsCount = 0;
     */
    var connectedNodes = new Set();

    graph.nodes.forEach(function (n) {
        idToNode[n.id] = n;
        /* DELETED
        //update the counter of sections
        if (n.sections[n.sections.length - 1] > sectionsCount) {
            sectionsCount = n.sections[n.sections.length - 1];
        }
        */
    });

    /* DELETED
    graph.nodes.forEach(function (n) {
        n.firstSection = n.sections[0];
    });
    */

    /* DELETED
    // Sort nodes by first appearance (section)
    graph.nodes.sort(function (a, b) {
        return sectionCompare(a.firstSection, b.firstSection);
    }).reverse();
    */

    // Sort nodes by first appearance (section)
    graph.nodes.sort(function (a, b) {
        return sectionCompare(a.id, b.id);
    }).reverse();



    graph.links.forEach(function (e) {
        e.source = idToNode[e.source];
        e.target = idToNode[e.target];
        connectedNodes.add(e.source);
        connectedNodes.add(e.target);

        /*DELETED
        // populate the table at the end of the page
        var table = document.getElementById("relationsTable");
        // Create an empty <tr> element and append it at end of the table
        var row = table.insertRow();
        // Insert new cells (<td> elements) in the row
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        // fill the new cells:
        cell1.innerHTML = e.source.name;
        cell2.innerHTML = e.target.name;
        */

        /*
        if (e.source.firstSection > e.target.firstSection) {
            cell3.innerHTML = 'backward';
        } else {
            cell3.innerHTML = 'forward';
        }
        */

        /*DELETED
        cell4.innerHTML = e.annotators.length;
        */
    });


    // Compute x,y coordinates (have a little extra separation when we switch volumes)
    for (i = 0, j = 0; i < graph.nodes.length; ++i) {
        node = graph.nodes[i];
        //console.log(node);
        if (i > 0 && graph.nodes[i-1].id !== node.id) ++j;
        //TODO increase empty space between nodes
        node.x = j * groupSep + i * (width - 4 * groupSep) / (graph.nodes.length - 1);
        //console.log(node.x);
        node.y = height;
    }

    /*DELETED
    nodeRadius.domain(d3.extent(graph.nodes, function (d) { return d.sections.length; }));
    linkWidth.domain(d3.extent(graph.links, function (d) { return d.annotators.length; }));
    */

    // build the arrow.
    svg.append("svg:defs").selectAll("marker")
        .data(["end"])      // Different link/path types can be defined here
        .enter().append("svg:marker")    // This section adds in the arrows
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");

    var link = svg.append('g')
        .attr('class', 'links')
        .selectAll('path')
        .data(graph.links)
        .enter().append('path')
        .attr('d', function (d) {
            //console.log(d.source.x);
            //FIXME: handle root node
            // handle in different ways edges between near or distant nodes
            if ( parseInt(d.source.id) - parseInt(d.target.id) === 1) {
                return ['M', d.source.x, height, 'H', d.target.x + 25]
                    .join(' ');
            }
            else if ( parseInt(d.target.id) - parseInt(d.source.id) === 1) {
                return ['M', d.source.x, height, 'H', d.target.x - 5]
                    .join(' ');
            }
            else {
                return ['M', d.source.x, height, 'A', // A: elliptical arc
                    (d.source.x - d.target.x)/1.5, ',', // restore to /2 to make taller arcs
                    (d.source.x - d.target.x)/1.5, 0, 0, ',', // restore to /2 to make taller arcs
                    d.source.x < d.target.x ? 1 : 0, d.target.x, ',', height]
                    .join(' ');
            }
        })
        /*DELETED
        .attr('stroke-width', function (d) { return linkWidth(d.annotators.length); })
        */
        .attr('stroke-width', 2)
        .attr("marker-end", "url(#end)")
        .attr('id', function (d) { return 'path' + graph.links.indexOf(d).toString(); })
        //.attr('rel', function (d) { return 'path: '+d.source.name+' --> '+d.target.name; })
        .attr('class', function (d) {
            /* DELETED
            if (d.source.firstSection > d.target.firstSection) {
                return 'backward'
            }
            else {
                return 'forward'
            }
            */
        })
        .on('mouseover', function (d) {
            let currPath = d3.select(this).attr('id').replace("path", "");
            link.style('stroke', 'white');
            d3.select(this).style('stroke', 'black');
            d3.selectAll(".edgelabel").attr('fill', 'white');
            d3.selectAll("#edgelabel" + currPath).attr('fill', 'black');
            //TODO: hide markers
            //d3.selectAll("marker").attr('fill', 'white');

            // use different colors according to the direction of the edge
            /* DELETED
            if (d.source.firstSection > d.target.firstSection) {
                // backward edge
                d3.select(this).style('stroke', '#d62333');
            } else {
                // forward edge
                d3.select(this).style('stroke', '#0f0dd9');
            }
            */

            node.style('fill', function (node_d) {
                return node_d === d.source || node_d === d.target ? null : 'white';
            });
            node.attr('stroke', function (node_d) {
                return node_d === d.source || node_d === d.target ? "black" : 'white';
            });
        })
        .on('mouseout', function (d) {
            link.style('stroke', null);
            node.style('fill', null);
            node.attr('stroke', 'black');
            d3.selectAll(".edgelabel").attr('fill', 'black');
        });

    var node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('rect')
        .data(graph.nodes)
        .enter().append('rect')
        .attr('x', function (d) { return d.x - 10; }) // FIXME: don't use magic numbers
        .attr('y', function (d) { return d.y ; })
        /* DELETED
        .attr('r', function (d) { return nodeRadius(d.sections.length); })
        */
        //.attr('r', 7)
        .attr("width", rectWidth)
        .attr("height", rectHeight)
        .attr('id', function (d) { return 'node: '+d.name; })
        .attr('stroke', 'black')
        .attr('stroke-width', 2)
        .attr('fill', function (d) { return colors(d.pos);})
        .on('mouseover', function (d) {
            //node.style('fill', null);
            var nodesToHighlight = graph.links.map(function (e) { return e.source === d ? e.target : e.target === d ? e.source : 0})
                .filter(function (d) { return d; });
            // include the selected node in the group to highlight
            nodesToHighlight.push(d);

            node.filter(function (d) { return nodesToHighlight.indexOf(d) < 0; })
                .attr('stroke', 'white')
                .style('fill', 'white');

            link.style('stroke', function (e) { return (e.source === d || e.target === d) ? "null" : "white"});

            var edgesToHighlight = graph.links.filter(function (e) { return (e.source === d || e.target === d) })
            // FIXME: add programmatically a "rel_id" field to every relation in the json
                .map(function (d) { console.log(d); return d.rel_id; });
            console.log(edgesToHighlight);

            d3.selectAll(".edgelabel").attr('fill', 'white');
            //d3.selectAll("#edgelabel" + currPath).attr('fill', 'black');

            /* DELETED
            link.style('stroke', function (link_d) {
                var color = null;

                // use different colors according to the direction of the edge
                if (link_d.source.firstSection > link_d.target.firstSection) {
                    // backward edge
                    color = '#d62333';
                } else {
                    // forward edge
                    color = '#0f0dd9';
                };
                return link_d.source === d | link_d.target === d ? color : null;
            });
            */
        })
        .on('mouseout', function (d) {
            node.style('fill', null);
            node.attr('stroke', 'black');
            link.style('stroke', null);
            d3.selectAll(".edgelabel").attr('fill', 'black');
        });

        /*DELETED
        // TODO: filter the graph by selecting a node
        .on('click', function (d) {
            //d3.select(this).classed("selected", !d3.select(this).classed("selected"));
            node.style('fill', null);
            var currNode = this.id;
            d3.select(this).style('fill', 'yellow');
            link.filter(function (d) { return ("node: " + d.source.name) === currNode; })
                .style('fill', 'reds');
        });
        */


    var wordLabels = svg.selectAll(".wordlabel")
        .data(graph.nodes);

    // add words near the rects
    wordLabels.enter()
        .append("text")
        .attr('x', function (d) { return d.x - 10; })
        .attr('y', function (d) { return d.y + rectHeight + 15; })
        .attr("font-size", wordFontSize.toString() + "px")
        .text(function(d) {return d.name;});

    var posLabels = svg.selectAll(".poslabel")
        .data(graph.nodes);

    // add POS inside rects
    posLabels.enter()
        .append("text")
        .attr('x', function (d) { return d.x; })
        .attr('y', function (d) { return d.y + rectHeight - 4; })
        .attr("font-size", posFontSize.toString() + "px")
        .text(function(d) {return d.pos;});


    // add edge labels
    var edgelabels = svg.selectAll(".edgelabel")
        .data(graph.links);

    edgelabels.enter()
        .append("text")
        // uncomment these lines if you want a basic style for edge labels (and delete the append("textPath) and the next one with href)
        //.attr('x', function (d) { return d.source.x + (d.target.x - d.source.x)/2; })
        //.attr('y', function (d) { return d.source.y + (d.target.y - d.source.y)/2; })
        .attr("dy", function (d) { return d.source.id > d.target.id ? 12 : -5; })
        .attr("text-anchor", "middle")
        .attr("font-size", edgeFontSize + "px")
        .attr('class','edgelabel')
        .attr('id', function (d,i) { return 'edgelabel'+i; })
        .append("textPath")
        .attr("startOffset", "50%")
        .attr("xlink:href", function (d, i) { return '#path' + i; })
        .text(function(d) {return d.name;});

    //FIXME: next lines are for reverse upside down edgelabels
    var reverseTextPaths = svg.selectAll("textPath").filter(function(d, i){ return d.source.id > d.target.id; })
        .attr("transform", "rotate(180)");

    //console.log(reverseTextPaths);


    // add text box for mouse-hover
    node.append('title').text(function (d) { return d.name;});
    link.append('title').text(function (d) { return d.source.name + ' (' + d.source.pos + ')' +  ' --> ' + d.target.name  + ' (' + d.target.pos + ')';});

    function sectionCompare (sectionA, sectionB) {
        if (sectionA != sectionB)
            return sectionB - sectionA;

        return 0;
    }
});
