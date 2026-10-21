# Zomato Power BI dashboard

Open `zomato_2.pbip` with Power BI Desktop. The project contains five report pages, each with three analytical visuals and interactive slicers for city tier, road traffic, and festival conditions.

## Pages

1. **Executive Command Center** — daily demand trend, city-tier order mix, and order-type/festival performance.
2. **Bottleneck Explorer** — weather comparison, an interactive weather × traffic matrix, and traffic volume versus duration.
3. **Fleet Performance Lab** — fleet mix, vehicle-condition impact by vehicle type, and partner rating versus speed.
4. **Logistics & Demand Simulator** — distance/time scatter, hourly demand versus duration, and preparation versus delivery time.
5. **Partner & Decision Studio** — day/city performance, batching penalty by festival status, and partner age versus duration.

## Interactive behavior

- Use the four page-specific slicers at the top of every page to change the analysis context.
- Select a bar, column, line, or area segment to cross-filter the other visuals on that page.
- On the scatter pages, select a point or category to isolate a city, partner, or route pattern.
- Use the visual header eraser to clear a selection.

## Data source

The semantic model imports `cleaned_zomato_data.csv` from the `powerbi` folder. Power BI Desktop requires `File.Contents` to receive an absolute path, so this project is currently configured for the authoring machine path. If you move the folder to another computer, open the semantic model's M expression and replace the CSV path with the new absolute path to `powerbi/cleaned_zomato_data.csv`.
