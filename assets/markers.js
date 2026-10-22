window.couriers = {
  pointToLayer: function (feature, latlng) {
    return L.circleMarker(latlng, {
      radius: 6,
      color: feature.properties.color,
      weight: 1,
      fillOpacity: 0.7,
    });
  },
};
