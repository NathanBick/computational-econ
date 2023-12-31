library(ggplot2)
library(dplyr)
options(scipen=999)

# read in the data
simulation_data <- read.csv("simulation_data.csv", header = TRUE)

# make the data long on money, happiness
simulation_data_long <- simulation_data %>%
    tidyr::gather(key = "variable", value = "value", hours, free, work, money, happiness)

# calculate the total amount of money, time, and happiness for each type in each step
simulation_data_long_totals <- simulation_data_long %>%
    group_by(type, variable, step) %>%
    summarise(value = sum(value))

# add across type as well
simulation_data_long_totals2 <- simulation_data_long_totals %>%
    group_by(variable, step) %>%
    summarise(value = sum(value))

simulation_data_long_totals2 %>%
    ggplot(aes(x=step, y=value, color=variable)) +
    geom_line() +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Total value")
    
# plot the means amount of money, time, and happiness for each type in each step
p <- simulation_data_long %>%
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
p_tot <- simulation_data_long_totals %>%
    ggplot(aes(x = step, y = value, color = variable)) +
    geom_line() +
    facet_wrap(~type, ncol = 1) +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Total value")

# open p in a new window
ggsave("plots/plot_tot.png", p_tot, width = 10, height = 10, units = "in", dpi = 300)

# plot distribution of happiness for each type and step
p_happy <- simulation_data_long %>%
    filter(variable == "happiness") %>%
    ggplot(aes(x = value, color = type)) +
    geom_density(alpha=0.5, ) +
    facet_grid(~step) +
    theme_bw() +
    labs(x = "Happiness", y = "Count")

# save
ggsave("plots/plot_happy.png", p_happy, width = 10, height = 10, units = "in", dpi = 300)

# focus on hours now
# plot free, work, hours for each type in each step
time <- simulation_data_long %>%
    filter(variable %in% c("hours","free","work")) %>% 
    group_by(type, variable, step) %>%
    summarise(value = mean(value)) %>%
    ggplot(aes(x = step, y = value, color = variable)) +
    geom_line() +
    facet_grid(type ~ ., scales = "free_y") +
    theme_bw() +
    theme(legend.position = "bottom") +
    labs(x = "Step", y = "Hours")

# save
ggsave("plots/plot_hours.png", time, width = 10, height = 10, units = "in", dpi = 300)

# get distribution of money and happiness at the beginning of the simulation
simulation_data %>%
    filter(step == 0) %>%
    ggplot(aes(x = money)) +
    geom_histogram(bins = 100) +
    facet_grid(~type) +
    theme_bw() +
    labs(x = "Money", y = "Count")

# transaction data
transaction_data <- read.csv("transactions.csv", header = TRUE)

# plot the average transaction amount for each step
t <- transaction_data %>%
    group_by(step) %>%
    summarise(mean = mean(price)) %>%
    ggplot(aes(x = step, y = mean)) +
    geom_line() +
    theme_bw() +
    labs(x = "Step", y = "Mean Price")

ggsave("plots/plot_transaction.png", t, width = 10, height = 10, units = "in", dpi = 300)

# count of transactions in each step
t2 <- transaction_data %>%
    group_by(step) %>%
    summarise(count = n()) %>%
    ggplot(aes(x = step, y = count)) +
    geom_line() +
    theme_bw() +
    labs(x = "Step", y = "Number of transactions")

ggsave("plots/plot_transaction_count.png", t2, width = 10, height = 10, units = "in", dpi = 300)