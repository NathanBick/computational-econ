library(ggplot2)
library(dplyr)
options(scipen=999)

# read in the data
data <- read.csv("simulation_data.csv", header = TRUE)

# make the data long on money, happiness
data_long <- data %>%
    tidyr::gather(key = "variable", value = "value", hours, free, work, money, happiness)

# calculate the total amount of money, time, and happiness for each type in each step
data_long_totals <- data_long %>%
    group_by(type, variable, step) %>%
    summarise(value = sum(value))

# add across type as well
data_long_totals2 <- data_long_totals %>%
    group_by(variable, step) %>%
    summarise(value = sum(value))

data_long_totals2 %>%
    ggplot(aes(x=step, y=value, color=variable)) +
    geom_line() +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Total value")
    
# plot the means amount of money, time, and happiness for each type in each step
p <- data_long %>%
    group_by(type, variable, step) %>%
    summarise(mean = mean(value)) %>%
    ggplot(aes(x = step, y = mean, color = variable)) +
    geom_line() +
    facet_wrap(~type, ncol = 1) +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Mean value")

# open p in a new window
ggsave("plots/plot.png", p, width = 10, height = 10, units = "in", dpi = 300)

# plot the totals
p_tot <- data_long_totals %>%
    ggplot(aes(x = step, y = value, color = variable)) +
    geom_line() +
    facet_wrap(~type, ncol = 1) +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Total value")

# open p in a new window
ggsave("plots/plot_tot.png", p_tot, width = 10, height = 10, units = "in", dpi = 300)

# focus on hours now
# plot free, work, hours for each type in each step
time <- data_long %>%
    filter(variable %in% c("hours","free","work")) %>%
    ggplot(aes(x = step, y = value, color = variable)) +
    geom_line() +
    facet_grid(type ~ ., scales = "free_y") +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Hours")

# save
ggsave("plots/plot_hours.png", time, width = 10, height = 10, units = "in", dpi = 300)

# get distribution of money and happiness at the beginning of the simulation
data %>%
    filter(step == 0) %>%
    ggplot(aes(x = money)) +
    geom_histogram(bins = 100) +
    facet_grid(~type) +
    theme_bw() +
    labs(x = "Money", y = "Count")
